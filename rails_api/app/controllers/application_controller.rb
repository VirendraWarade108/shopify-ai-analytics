class ApplicationController < ActionController::API
  include ActionController::Cookies
  include ActionController::RequestForgeryProtection
  
  # CSRF protection for session-based requests
  protect_from_forgery with: :null_session, if: -> { request.format.json? }
  
  # Standard error handling
  rescue_from StandardError, with: :handle_standard_error
  rescue_from ActiveRecord::RecordNotFound, with: :handle_not_found
  rescue_from ActionController::ParameterMissing, with: :handle_parameter_missing
  
  before_action :log_request
  after_action :log_response

  protected

  # Get current shop from session or header
  def current_shop
    return @current_shop if defined?(@current_shop)
    
    shop_domain = session[:shop_domain] || request.headers['X-Shop-Domain']
    @current_shop = Shop.find_by(shopify_domain: shop_domain) if shop_domain.present?
  end

  # Require authenticated shop
  def require_shop
    unless current_shop
      render json: { 
        error: 'Unauthorized', 
        message: 'Shop authentication required. Please authenticate via /auth/shopify' 
      }, status: :unauthorized
    end
  end

  # Demo mode check
  def demo_mode?
    ENV.fetch('DEMO_MODE', 'false').downcase == 'true'
  end

  # Render success response with consistent format
  def render_success(data, status: :ok, message: nil)
    response = {
      success: true,
      data: data
    }
    response[:message] = message if message.present?
    
    render json: response, status: status
  end

  # Render error response with consistent format
  def render_error(message, status: :unprocessable_entity, errors: nil)
    response = {
      success: false,
      error: message
    }
    response[:errors] = errors if errors.present?
    
    render json: response, status: status
  end

  private

  # Error handlers
  def handle_standard_error(exception)
    Rails.logger.error("Unhandled error: #{exception.class} - #{exception.message}")
    Rails.logger.error(exception.backtrace.join("\n"))
    
    render_error(
      'An unexpected error occurred',
      status: :internal_server_error,
      errors: Rails.env.development? ? { 
        message: exception.message, 
        backtrace: exception.backtrace.first(10) 
      } : nil
    )
  end

  def handle_not_found(exception)
    render_error(
      exception.message,
      status: :not_found
    )
  end

  def handle_parameter_missing(exception)
    render_error(
      "Missing required parameter: #{exception.param}",
      status: :bad_request
    )
  end

  # Logging
  def log_request
    Rails.logger.info({
      event: 'request_started',
      method: request.method,
      path: request.path,
      params: filtered_params,
      ip: request.remote_ip,
      user_agent: request.user_agent,
      request_id: request.uuid
    }.to_json)
  end

  def log_response
    Rails.logger.info({
      event: 'request_completed',
      method: request.method,
      path: request.path,
      status: response.status,
      request_id: request.uuid,
      duration_ms: (Time.current - @request_start_time) * 1000 if @request_start_time
    }.to_json)
  end

  def filtered_params
    request.params.except('controller', 'action', 'format')
  end

  # Set request start time
  def set_request_start_time
    @request_start_time = Time.current
  end
end