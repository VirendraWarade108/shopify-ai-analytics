require_relative "boot"

require "rails"
# Pick the frameworks you want:
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
# require "rails/test_unit/railtie"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module ShopifyAnalyticsApi
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 7.1

    # Configuration for the application, engines, and railties goes here.
    #
    # These settings can be overridden in specific environments using the files
    # in config/environments, which are processed later.
    #
    # config.time_zone = "Central Time (US & Canada)"
    # config.eager_load_paths << Rails.root.join("extras")

    # Only loads a smaller set of middleware suitable for API only apps.
    # Middleware like session, flash, cookies can be added back manually.
    # Skip views, helpers and assets when generating a new resource.
    config.api_only = true

    # Use SQL instead of Active Record schema dumper when creating database
    config.active_record.schema_format = :sql

    # Configure session store for Shopify OAuth
    config.session_store :cookie_store, key: '_shopify_analytics_session'
    
    # Add session middleware back (needed for OAuth)
    config.middleware.use ActionDispatch::Cookies
    config.middleware.use config.session_store, config.session_options

    # Configure CORS
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
      g.fixture_replacement :factory_bot
      g.factory_bot dir: 'spec/factories'
      g.skip_routes false
      g.helper false
      g.assets false
    end

    # Autoload lib directory
    config.autoload_paths << Rails.root.join('lib')
    config.eager_load_paths << Rails.root.join('lib')

    # Configure log formatting
    config.log_formatter = ::Logger::Formatter.new
    
    # Use JSON format for logs in production
    if ENV['RAILS_ENV'] == 'production'
      config.log_formatter = proc do |severity, datetime, progname, msg|
        {
          timestamp: datetime.iso8601,
          severity: severity,
          message: msg,
          progname: progname
        }.to_json + "\n"
      end
    end

    # Configure time zone
    config.time_zone = 'UTC'
    config.active_record.default_timezone = :utc

    # Configure cache store
    config.cache_store = :memory_store, { size: 64.megabytes }
  end
end