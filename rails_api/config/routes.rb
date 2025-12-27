Rails.application.routes.draw do
  # Health check endpoint
  get '/health', to: proc { [200, { 'Content-Type' => 'text/plain' }, ['OK']] }

  # Shopify OAuth routes
  get '/auth/shopify', to: 'shopify_auth#authenticate'
  get '/auth/shopify/callback', to: 'shopify_auth#callback'
  post '/auth/shopify/uninstall', to: 'shopify_auth#uninstall'

  # API routes
  namespace :api do
    namespace :v1 do
      # Main analytics query endpoint
      post '/questions', to: 'questions#create'
      
      # Query history
      get '/questions', to: 'questions#index'
      get '/questions/:id', to: 'questions#show'
      
      # Shop information
      get '/shop', to: 'questions#shop_info'
    end
  end

  # Webhooks (optional for production use)
  post '/webhooks/app_uninstalled', to: 'webhooks#app_uninstalled'

  # Root route
  root to: proc { 
    [200, 
     { 'Content-Type' => 'application/json' }, 
     [{
       service: 'Shopify Analytics AI - Rails API',
       version: '1.0.0',
       status: 'running',
       endpoints: {
         health: '/health',
         auth: '/auth/shopify',
         questions: '/api/v1/questions'
       }
     }.to_json]
    ] 
  }
end