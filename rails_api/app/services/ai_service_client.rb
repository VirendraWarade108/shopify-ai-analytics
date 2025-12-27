class AiServiceClient
  class ServiceError < StandardError; end
  class TimeoutError < ServiceError; end
  class ConnectionError < ServiceError; end

  AI_SERVICE_URL = ENV.fetch('AI_SERVICE_URL', 'http://localhost:8000')
  TIMEOUT = ENV.fetch('AI_SERVICE_TIMEOUT', 120).to_i

  class << self
    # Process a question through the AI service
    def process_question(question:, shop_domain:, access_token:)
      Rails.logger.info("Calling AI service for question: #{question[0..50]}...")

      response = make_request(
        method: :post,
        path: '/api/v1/query',
        body: {
          question: question,
          shop_domain: shop_domain,
          access_token: access_token,
          context: {
            timestamp: Time.current.iso8601,
            demo_mode: demo_mode?
          }
        }
      )

      parse_response(response)
    rescue Faraday::TimeoutError => e
      Rails.logger.error("AI service timeout: #{e.message}")
      raise TimeoutError, "AI service request timed out after #{TIMEOUT} seconds"
    rescue Faraday::ConnectionFailed => e
      Rails.logger.error("AI service connection failed: #{e.message}")
      raise ConnectionError, "Could not connect to AI service at #{AI_SERVICE_URL}"
    rescue => e
      Rails.logger.error("AI service error: #{e.class} - #{e.message}")
      raise ServiceError, "AI service error: #{e.message}"
    end

    # Health check for AI service
    def health_check
      response = make_request(
        method: :get,
        path: '/health',
        timeout: 5
      )

      if response.success?
        { status: 'healthy', data: JSON.parse(response.body) }
      else
        { status: 'unhealthy', error: response.body }
      end
    rescue => e
      { status: 'unreachable', error: e.message }
    end

    # Get AI service version info
    def version_info
      response = make_request(
        method: :get,
        path: '/',
        timeout: 5
      )

      JSON.parse(response.body)
    rescue => e
      Rails.logger.error("Failed to get AI service version: #{e.message}")
      { error: e.message }
    end

    private

    def make_request(method:, path:, body: nil, timeout: TIMEOUT)
      connection = Faraday.new(url: AI_SERVICE_URL) do |conn|
        conn.request :json
        conn.response :json
        conn.adapter Faraday.default_adapter
        conn.options.timeout = timeout
        conn.options.open_timeout = 10
      end

      case method
      when :get
        connection.get(path)
      when :post
        connection.post(path, body)
      when :put
        connection.put(path, body)
      when :delete
        connection.delete(path)
      else
        raise ArgumentError, "Unsupported HTTP method: #{method}"
      end
    end

    def parse_response(response)
      unless response.success?
        error_msg = extract_error_message(response)
        raise ServiceError, "AI service returned error (#{response.status}): #{error_msg}"
      end

      body = response.body
      
      # Handle string response
      if body.is_a?(String)
        begin
          body = JSON.parse(body)
        rescue JSON::ParserError => e
          Rails.logger.error("Failed to parse AI service response: #{e.message}")
          raise ServiceError, "Invalid JSON response from AI service"
        end
      end

      # Validate response structure
      validate_response_structure(body)

      body
    end

    def extract_error_message(response)
      return response.reason_phrase if response.body.blank?

      body = response.body
      body = JSON.parse(body) if body.is_a?(String) rescue body

      if body.is_a?(Hash)
        body['error'] || body['message'] || body['detail'] || response.reason_phrase
      else
        response.reason_phrase
      end
    end

    def validate_response_structure(body)
      unless body.is_a?(Hash)
        raise ServiceError, "Expected JSON object response, got #{body.class}"
      end

      # Check for required fields
      required_fields = %w[status]
      missing_fields = required_fields - body.keys.map(&:to_s)
      
      if missing_fields.any?
        Rails.logger.warn("AI service response missing fields: #{missing_fields.join(', ')}")
      end

      # Check status
      if body['status'] == 'error' || body['status'] == 'failed'
        error_msg = body['error'] || body['message'] || 'Unknown error'
        raise ServiceError, "AI service processing failed: #{error_msg}"
      end
    end

    def demo_mode?
      ENV.fetch('DEMO_MODE', 'false').downcase == 'true'
    end
  end
end