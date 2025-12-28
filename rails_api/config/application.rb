require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "active_storage/engine"
require "action_controller/railtie"
require "action_mailer/railtie"
require "action_mailbox/engine"
require "action_text/engine"
require "action_view/railtie"
require "action_cable/engine"

Bundler.require(*Rails.groups)

module ShopifyAnalyticsApi
  class Application < Rails::Application
    # Initialize configuration defaults for Rails 8.0
    config.load_defaults 8.0

    # API-only application
    config.api_only = true

    # Autoload lib directory
    config.autoload_lib(ignore: %w[assets tasks])

    # Session configuration for OAuth
    config.session_store :cookie_store, 
      key: '_shopify_analytics_session',
      same_site: :lax,
      secure: Rails.env.production?,
      httponly: true

    # Add session middleware
    config.middleware.use ActionDispatch::Cookies
    config.middleware.use config.session_store, config.session_options

    # CORS Configuration
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins ENV.fetch('CORS_ORIGINS', 'http://localhost:3001').split(',')
        
        resource '*',
          headers: :any,
          methods: [:get, :post, :put, :patch, :delete, :options, :head],
          credentials: true,
          expose: ['Authorization']
      end
    end

    # Configure generators
    config.generators do |g|
      g.test_framework :rspec
      g.skip_routes false
      g.helper false
      g.assets false
    end

    # Time zone
    config.time_zone = 'UTC'
    config.active_record.default_timezone = :utc

    # Configure cache store
    config.cache_store = :memory_store, { size: 64.megabytes }

    # Logging
    config.log_level = ENV.fetch('RAILS_LOG_LEVEL', 'info').to_sym
    config.log_tags = [:request_id, :remote_ip]
  end
end