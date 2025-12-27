# CORS configuration for cross-origin requests
# This initializer configures Cross-Origin Resource Sharing (CORS)
# to allow the frontend application to communicate with the API

Rails.application.config.middleware.insert_before 0, Rack::Cors do
  allow do
    # Parse allowed origins from environment variable
    origins_list = ENV.fetch('CORS_ORIGINS', 'http://localhost:3001').split(',').map(&:strip)
    
    origins(*origins_list)

    resource '*',
      headers: :any,
      methods: [:get, :post, :put, :patch, :delete, :options, :head],
      credentials: true,
      expose: ['Authorization', 'X-Request-Id', 'X-Runtime'],
      max_age: 600

    # Additional CORS configuration for Shopify OAuth callback
    resource '/auth/*',
      headers: :any,
      methods: [:get, :post, :options],
      credentials: true,
      expose: ['Set-Cookie']
  end

  # Allow all origins in development mode for easier testing
  if Rails.env.development?
    allow do
      origins '*'
      
      resource '/health',
        headers: :any,
        methods: [:get, :options],
        credentials: false
    end
  end
end