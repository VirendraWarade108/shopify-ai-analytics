class ShopifyAuthController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:callback, :uninstall]

  # GET /auth/shopify
  # Initiates Shopify OAuth flow
  def authenticate
    shop = params[:shop]
    
    if shop.blank?
      return render_error('Shop parameter is required', status: :bad_request)
    end

    # Sanitize shop domain
    shop = sanitize_shop_domain(shop)
    
    # In demo mode, skip OAuth and create a demo shop
    if demo_mode?
      return handle_demo_authentication(shop)
    end

    # Build OAuth authorization URL
    scope = ShopifyApp.configuration.scope
    redirect_uri = "#{ENV.fetch('APP_URL')}/auth/shopify/callback"
    state = SecureRandom.hex(16)
    
    # Store state in session for verification
    session[:oauth_state] = state
    session[:shop_domain] = shop

    auth_url = "https://#{shop}/admin/oauth/authorize?" + {
      client_id: ShopifyApp.configuration.api_key,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    }.to_query

    render json: { 
      success: true,
      auth_url: auth_url,
      message: 'Redirect to auth_url to complete authentication'
    }
  end

  # GET /auth/shopify/callback
  # Handles OAuth callback from Shopify
  def callback
    shop = params[:shop]
    code = params[:code]
    state = params[:state]

    # Validate parameters
    if shop.blank? || code.blank?
      return render_error('Missing required OAuth parameters', status: :bad_request)
    end

    # Verify state to prevent CSRF
    if state != session[:oauth_state]
      return render_error('Invalid OAuth state', status: :unauthorized)
    end

    # Sanitize shop domain
    shop = sanitize_shop_domain(shop)

    begin
      # Exchange code for access token
      token = exchange_code_for_token(shop, code)

      # Create or update shop record
      shop_record = Shop.find_or_initialize_by(shopify_domain: shop)
      shop_record.shopify_token = token
      shop_record.save!

      # Store shop in session
      session[:shop_domain] = shop

      Rails.logger.info("Shop authenticated successfully: #{shop}")

      # Redirect to frontend or return success
      if params[:redirect_to].present?
        redirect_to params[:redirect_to], allow_other_host: true
      else
        render json: {
          success: true,
          message: 'Authentication successful',
          shop: {
            domain: shop_record.shopify_domain,
            id: shop_record.id
          }
        }
      end
    rescue => e
      Rails.logger.error("OAuth callback error: #{e.message}")
      render_error('Authentication failed', status: :internal_server_error)
    end
  end

  # POST /auth/shopify/uninstall
  # Handles app uninstallation webhook
  def uninstall
    shop_domain = params[:shop_domain] || shopify_webhook_shop_domain

    if shop_domain.present?
      shop = Shop.find_by(shopify_domain: shop_domain)
      if shop
        shop.update(shopify_token: nil, active: false)
        Rails.logger.info("Shop uninstalled: #{shop_domain}")
      end
    end

    head :ok
  end

  private

  def sanitize_shop_domain(shop)
    shop = shop.to_s.strip.downcase
    shop = shop.gsub(/\Ahttps?:\/\//, '')
    shop = shop.split('/').first
    shop = "#{shop}.myshopify.com" unless shop.include?('.')
    shop
  end

  def handle_demo_authentication(shop)
    # Create demo shop without real OAuth
    shop_record = Shop.find_or_create_by(shopify_domain: shop) do |s|
      s.shopify_token = "demo_token_#{SecureRandom.hex(16)}"
      s.active = true
    end

    session[:shop_domain] = shop

    render json: {
      success: true,
      message: 'Demo mode: Authentication simulated successfully',
      shop: {
        domain: shop_record.shopify_domain,
        id: shop_record.id
      },
      demo_mode: true
    }
  end

  def exchange_code_for_token(shop, code)
    # Make request to Shopify to exchange code for access token
    response = Faraday.post("https://#{shop}/admin/oauth/access_token") do |req|
      req.headers['Content-Type'] = 'application/json'
      req.body = {
        client_id: ShopifyApp.configuration.api_key,
        client_secret: ShopifyApp.configuration.secret,
        code: code
      }.to_json
    end

    if response.success?
      JSON.parse(response.body)['access_token']
    else
      raise "Token exchange failed: #{response.body}"
    end
  end

  def shopify_webhook_shop_domain
    # Extract shop domain from webhook headers
    request.headers['HTTP_X_SHOPIFY_SHOP_DOMAIN']
  end
end