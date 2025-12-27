class Shop < ApplicationRecord
  # Associations
  has_many :analytics_queries, dependent: :destroy

  # Validations
  validates :shopify_domain, presence: true, uniqueness: true
  validates :shopify_domain, format: { 
    with: /\A[a-z0-9\-]+\.myshopify\.com\z/i,
    message: "must be a valid Shopify domain"
  }

  # Lockbox encryption for access token
  encrypts :shopify_token, deterministic: false

  # Scopes
  scope :active, -> { where(active: true) }
  scope :inactive, -> { where(active: false) }
  scope :with_token, -> { where.not(shopify_token: nil) }

  # Callbacks
  before_validation :normalize_domain
  after_create :log_shop_installation
  after_update :log_token_changes

  # Instance methods

  # Check if shop has valid authentication
  def authenticated?
    shopify_token.present? && active?
  end

  # Get shop identifier for logging
  def identifier
    shopify_domain
  end

  # Check if shop is in demo mode
  def demo_shop?
    shopify_domain == 'demo.myshopify.com' || shopify_token&.start_with?('demo_')
  end

  # Get Shopify API client (for future use)
  def api_client
    return nil unless authenticated?
    
    @api_client ||= begin
      ShopifyAPI::Context.setup(
        api_key: ENV['SHOPIFY_API_KEY'],
        api_secret_key: ENV['SHOPIFY_API_SECRET'],
        host: shopify_domain,
        scope: ENV.fetch('SHOPIFY_SCOPES', 'read_products,read_orders'),
        is_embedded: false,
        api_version: '2024-01'
      )
      
      session = ShopifyAPI::Auth::Session.new(
        shop: shopify_domain,
        access_token: shopify_token
      )
      
      ShopifyAPI::Clients::Rest::Admin.new(session: session)
    rescue => e
      Rails.logger.error("Failed to create Shopify API client: #{e.message}")
      nil
    end
  end

  # Get query statistics
  def query_stats
    {
      total_queries: analytics_queries.count,
      successful_queries: analytics_queries.where(status: 'completed').count,
      failed_queries: analytics_queries.where(status: 'failed').count,
      pending_queries: analytics_queries.where(status: 'pending').count,
      average_confidence: analytics_queries.where(status: 'completed').average(:confidence_score)&.round(2),
      last_query_at: analytics_queries.maximum(:created_at)
    }
  end

  # Deactivate shop (on uninstall)
  def deactivate!
    update!(active: false, shopify_token: nil)
    Rails.logger.info("Shop deactivated: #{shopify_domain}")
  end

  # Reactivate shop
  def reactivate!(token)
    update!(active: true, shopify_token: token)
    Rails.logger.info("Shop reactivated: #{shopify_domain}")
  end

  private

  def normalize_domain
    return if shopify_domain.blank?
    
    # Remove protocol
    self.shopify_domain = shopify_domain.gsub(/\Ahttps?:\/\//, '')
    
    # Remove trailing slashes
    self.shopify_domain = shopify_domain.gsub(/\/\z/, '')
    
    # Convert to lowercase
    self.shopify_domain = shopify_domain.downcase
    
    # Add .myshopify.com if not present
    unless shopify_domain.include?('.')
      self.shopify_domain = "#{shopify_domain}.myshopify.com"
    end
  end

  def log_shop_installation
    Rails.logger.info({
      event: 'shop_installed',
      shop_domain: shopify_domain,
      shop_id: id,
      demo: demo_shop?
    }.to_json)
  end

  def log_token_changes
    if saved_change_to_shopify_token?
      if shopify_token.present?
        Rails.logger.info("Shop token updated: #{shopify_domain}")
      else
        Rails.logger.info("Shop token removed: #{shopify_domain}")
      end
    end

    if saved_change_to_active?
      status = active? ? 'activated' : 'deactivated'
      Rails.logger.info("Shop #{status}: #{shopify_domain}")
    end
  end
end