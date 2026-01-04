# CORS configuration for cross-origin requests
Rails.application.config.middleware.insert_before 0, Rack::Cors do
  # Development mode - allow all origins
  if Rails.env.development?
    allow do
      origins '*'  # Allow any origin

      resource '*',
        headers: :any,
        methods: [:get, :post, :put, :patch, :delete, :options, :head],
        credentials: false,  # IMPORTANT: Must be false with wildcard
        expose: ['Authorization', 'X-Request-Id', 'X-Runtime'],
        max_age: 600
    end
  else
    # Production: Use specific origins with credentials
    allow do
      origins_list = ENV.fetch('CORS_ORIGINS', '').split(',').map(&:strip)
      origins(*origins_list)

      resource '*',
        headers: :any,
        methods: [:get, :post, :put, :patch, :delete, :options, :head],
        credentials: true,
        expose: ['Authorization', 'X-Request-Id', 'X-Runtime'],
        max_age: 600
    end
  end
end