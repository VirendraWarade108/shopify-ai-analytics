ShopifyApp.configure do |config|
  config.application_name = ENV.fetch('SHOPIFY_APP_NAME', 'Shopify Analytics AI')
  config.api_key = ENV.fetch('SHOPIFY_API_KEY', '')
  config.secret = ENV.fetch('SHOPIFY_API_SECRET', '')
  config.scope = ENV.fetch('SHOPIFY_SCOPES', 'read_products,read_orders,read_customers,read_analytics')

  config.embedded_app = false
  config.after_authenticate_job = false
  config.api_version = '2024-01'

  # Use your custom Shopify session store
  config.shop_session_repository = 'ShopifySessionStore'

  config.webhooks = [
    {
      topic: 'app/uninstalled',
      address: "#{ENV.fetch('APP_URL', 'http://localhost:3000')}/webhooks/app_uninstalled"
    }
  ]

  config.root_url = '/'
  config.login_url = '/auth/shopify'
end
