# Be sure to restart your server when you modify this file.

# Configure parameters to be filtered from the log file. Use this to limit dissemination of
# sensitive information. See the ActiveSupport::ParameterFilter documentation for supported
# notations and behaviors.

# Filter out sensitive parameters from logs
Rails.application.config.filter_parameters += [
  :passw, :secret, :token, :_key, :crypt, :salt, :certificate, :otp, :ssn,
  
  # Shopify-specific sensitive data
  :access_token,
  :shopify_token,
  :shopify_api_key,
  :shopify_api_secret,
  :shop_token,
  
  # API keys and secrets
  :api_key,
  :api_secret,
  :api_token,
  :auth_token,
  :authentication_token,
  :bearer_token,
  :client_secret,
  
  # Anthropic API
  :anthropic_api_key,
  :anthropic_key,
  
  # Encryption keys
  :lockbox_master_key,
  :master_key,
  :encryption_key,
  
  # User credentials
  :password,
  :password_confirmation,
  :current_password,
  :new_password,
  
  # Credit card data
  :card_number,
  :cvv,
  :cvc,
  :card_exp_month,
  :card_exp_year,
  
  # Personal identifiable information
  :email,
  :phone,
  :ssn,
  :social_security_number,
  :tax_id,
  
  # OAuth
  :oauth_token,
  :oauth_token_secret,
  :refresh_token,
  
  # Session data
  :session_id,
  :csrf_token,
  :authenticity_token,
]

# Example of filtering nested parameters
# Rails.application.config.filter_parameters += [:credit_card, { card: [:number, :cvv] }]

# Filter entire request bodies for certain paths (uncomment if needed)
# Rails.application.config.filter_parameters += [
#   ->(k, v) { v.replace("[FILTERED]") if k == "raw_post" && v.is_a?(String) }
# ]