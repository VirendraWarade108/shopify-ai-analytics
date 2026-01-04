class AnalyticsQuery < ApplicationRecord
  # Associations
  belongs_to :shop

  # Validations
  validates :question, presence: true, length: { minimum: 3, maximum: 1000 }
  validates :status, presence: true, inclusion: { 
    in: %w[pending processing completed failed],
    message: "%{value} is not a valid status"
  }
  validates :confidence_score, numericality: { 
    greater_than_or_equal_to: 0, 
    less_than_or_equal_to: 1,
    allow_nil: true 
  }

  # Scopes
  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  scope :pending, -> { where(status: 'pending') }
  scope :processing, -> { where(status: 'processing') }
  scope :high_confidence, -> { where('confidence_score >= ?', 0.8) }
  scope :low_confidence, -> { where('confidence_score < ?', 0.5) }
  scope :recent, -> { order(created_at: :desc) }
  scope :by_intent, ->(intent) { where("intent->>'domain' = ?", intent) }

  # Callbacks
  before_validation :set_default_status
  after_create :log_query_creation
  after_update :log_query_completion

  # Serialization for JSON fields
  #serialize :intent, coder: JSON
  #serialize :insights, coder: JSON
  #serialize :response_data, coder: JSON

  # Instance methods

  # Check if query was successful
  def successful?
    status == 'completed' && error_message.blank?
  end

  # Check if query is still in progress
  def in_progress?
    %w[pending processing].include?(status)
  end

  # Get intent domain (e.g., 'inventory', 'sales')
  def intent_domain
    intent&.dig('domain') || intent&.dig('intent_type') || 'unknown'
  end

  # Get intent confidence
  def intent_confidence
    intent&.dig('confidence') || 0.0
  end

  # Get summary from insights
  def summary
    insights&.dig('summary') || 'No summary available'
  end

  # Get key findings
  def key_findings
    insights&.dig('key_findings') || []
  end

  # Get recommendations
  def recommendations
    insights&.dig('recommendations') || []
  end

  # Get formatted response for API
  def to_api_response
    {
      id: id,
      question: question,
      status: status,
      intent: {
        domain: intent_domain,
        confidence: intent_confidence
      },
      query: shopifyql_query,
      insights: {
        summary: summary,
        key_findings: key_findings,
        recommendations: recommendations,
        data_summary: insights&.dig('data_summary') || {}
      },
      confidence: confidence_score,
      error: error_message,
      created_at: created_at,
      completed_at: updated_at,
      processing_time_ms: processing_time_ms
    }
  end

  # Calculate processing time
  def processing_time_ms
    return nil unless completed_at.present?
    ((completed_at - created_at) * 1000).round
  end

  # Mark as completed
  def mark_completed!(response_data)
    update!(
      status: 'completed',
      response_data: response_data,
      completed_at: Time.current
    )
  end

  # Mark as failed
  def mark_failed!(error)
    update!(
      status: 'failed',
      error_message: error.to_s,
      completed_at: Time.current
    )
  end

  # Get confidence level as text
  def confidence_level
    return 'unknown' if confidence_score.nil?
    
    case confidence_score
    when 0.8..1.0 then 'high'
    when 0.5...0.8 then 'medium'
    else 'low'
    end
  end

  # Check if query needs review (low confidence)
  def needs_review?
    completed? && confidence_score.present? && confidence_score < 0.5
  end

  private

  def set_default_status
    self.status ||= 'pending'
  end

  def log_query_creation
    Rails.logger.info({
      event: 'query_created',
      query_id: id,
      shop_id: shop_id,
      question: question,
      question_length: question.length
    }.to_json)
  end

  def log_query_completion
    return unless saved_change_to_status? && %w[completed failed].include?(status)
    
    Rails.logger.info({
      event: 'query_completed',
      query_id: id,
      shop_id: shop_id,
      status: status,
      confidence: confidence_score,
      processing_time_ms: processing_time_ms,
      intent_domain: intent_domain
    }.to_json)
  end

  def completed?
    status == 'completed'
  end
end