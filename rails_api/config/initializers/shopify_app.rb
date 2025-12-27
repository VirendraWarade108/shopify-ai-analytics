# Shopify App configuration
# This initializer sets up the Shopify OAuth flow and API connection

ShopifyApp.configure do |config|
  # Shopify API credentials from environment variables
  config.application_name = ENV.fetch('SHOPIFY_APP_NAME', 'Shopify Analytics AI')
  config.api_key = ENV.fetch('SHOPIFY_API_KEY', '')
  config.secret = ENV.fetch('SHOPIFY_API_SECRET', '')
  
  # OAuth scopes required for the app
  config.scope = ENV.fetch('SHOPIFY_SCOPES', 'read_products,read_orders,read_customers,read_analytics')
  
  # Redirect URL after OAuth
  config.embedded_app = false
  config.after_authenticate_job = false
  
  # API version
  config.api_version = '2024-01'
  
  # Shop model for storing shop data
  config.shop_session_repository = 'Shop'
  
  # Webhook configuration
  config.webhooks = [
    { topic: 'app/uninstalled', address: "#{ENV.fetch('APP_URL', 'http://localhost:3000')}/webhooks/app_uninstalled" }
  ]
  
  # Session storage
  config.session_repository = 'Shop'
  
  # Root URL for the app
  config.root_url = '/'
  
  # Login URL
  config.login_url = '/auth/shopify'
  
  # Allow JWT authentication
  config.allow_jwt_authentication = true
  config.allow_cookie_authentication = true
  
  # Custom session storage (we'll use database)
  config.custom_post_authenticate_tasks = lambda do |session|
    # Custom tasks after authentication if needed
    Rails.logger.info("Shop authenticated: #{session.shop}")
  end
  
  # Handle API version changes
  config.check_api_version_on_startup = false
end

# Monkey patch to make ShopifyApp work with our custom Shop model
module ShopifyApp
  module SessionRepository
    def self.retrieve(id)
      Shop.find_by(shopify_domain: id)
    end

    def self.store(session, *args)
      shop = Shop.find_or_initialize_by(shopify_domain: session.shop)
      shop.shopify_token = session.access_token
      shop.save!
      shop
    end

    def self.retrieve_by_shopify_user_id(user_id)
      nil
    end

    def self.destroy_by_shopify_user_id(user_id)
      # Not implemented for app-level tokens
    end
  end
end