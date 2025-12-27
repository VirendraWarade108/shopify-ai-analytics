module Api
  module V1
    class QuestionsController < ApplicationController
      before_action :require_shop, unless: :demo_mode?
      before_action :set_query, only: [:show]

      # POST /api/v1/questions
      # Main endpoint for processing analytics questions
      def create
        question_text = params.require(:question)
        
        Rails.logger.info("Processing question: #{question_text}")

        # Create query record
        query = AnalyticsQuery.create!(
          shop: current_shop || demo_shop,
          question: question_text,
          status: 'pending'
        )

        begin
          # Call AI service to process question
          ai_response = AiServiceClient.process_question(
            question: question_text,
            shop_domain: current_shop&.shopify_domain || 'demo.myshopify.com',
            access_token: current_shop&.shopify_token || 'demo_token'
          )

          # Update query with results
          query.update!(
            status: ai_response['status'] || 'completed',
            intent: ai_response['intent'],
            shopifyql_query: ai_response['query'],
            insights: ai_response['insights'],
            confidence_score: ai_response['confidence'],
            response_data: ai_response
          )

          render_success(
            {
              id: query.id,
              question: query.question,
              status: query.status,
              intent: query.intent,
              insights: query.insights,
              confidence: query.confidence_score,
              created_at: query.created_at
            },
            status: :created
          )

        rescue AiServiceClient::ServiceError => e
          query.update!(
            status: 'failed',
            error_message: e.message
          )
          
          Rails.logger.error("AI service error: #{e.message}")
          render_error(
            'Failed to process question',
            status: :service_unavailable,
            errors: { details: e.message }
          )

        rescue => e
          query.update!(
            status: 'failed',
            error_message: e.message
          )
          
          Rails.logger.error("Unexpected error: #{e.message}")
          render_error(
            'An error occurred while processing your question',
            status: :internal_server_error
          )
        end
      end

      # GET /api/v1/questions
      # List query history
      def index
        queries = if demo_mode?
                    AnalyticsQuery.order(created_at: :desc).limit(50)
                  else
                    current_shop.analytics_queries.order(created_at: :desc).limit(50)
                  end

        render_success(
          queries.map { |q|
            {
              id: q.id,
              question: q.question,
              status: q.status,
              confidence: q.confidence_score,
              created_at: q.created_at
            }
          }
        )
      end

      # GET /api/v1/questions/:id
      # Get specific query details
      def show
        render_success(
          {
            id: @query.id,
            question: @query.question,
            status: @query.status,
            intent: @query.intent,
            query: @query.shopifyql_query,
            insights: @query.insights,
            confidence: @query.confidence_score,
            error: @query.error_message,
            created_at: @query.created_at,
            updated_at: @query.updated_at
          }
        )
      end

      # GET /api/v1/shop
      # Get current shop information
      def shop_info
        if demo_mode?
          return render_success({
            domain: 'demo.myshopify.com',
            name: 'Demo Shop',
            demo_mode: true
          })
        end

        render_success({
          domain: current_shop.shopify_domain,
          id: current_shop.id,
          active: current_shop.active
        })
      end

      private

      def set_query
        @query = if demo_mode?
                   AnalyticsQuery.find(params[:id])
                 else
                   current_shop.analytics_queries.find(params[:id])
                 end
      end

      def demo_shop
        @demo_shop ||= Shop.find_or_create_by(shopify_domain: 'demo.myshopify.com') do |s|
          s.shopify_token = 'demo_token'
          s.active = true
        end
      end
    end
  end
end