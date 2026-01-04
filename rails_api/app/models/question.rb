class Question < ApplicationRecord
  belongs_to :shop
  
  # Validations
  validates :question_text, presence: true
  validates :status, presence: true, inclusion: { in: %w[pending processing completed failed] }
  
  # In Rails 8, JSON columns don't need serialize - they're automatically handled
  # Rails will automatically parse/serialize JSON columns
  
  # Enums
  enum :status, {
    pending: 'pending',
    processing: 'processing',
    completed: 'completed',
    failed: 'failed'
  }, default: 'pending'
  
  # Scopes
  scope :recent, -> { order(created_at: :desc) }
  scope :completed_successfully, -> { where(status: 'completed') }
  scope :failed_questions, -> { where(status: 'failed') }
  
  # Instance methods
  def mark_as_processing!
    update!(status: 'processing', processed_at: Time.current)
  end
  
  def mark_as_completed!(response_data)
    update!(
      status: 'completed',
      response: response_data,
      completed_at: Time.current
    )
  end
  
  def mark_as_failed!(error_message)
    update!(
      status: 'failed',
      error_message: error_message,
      completed_at: Time.current
    )
  end
  
  def processing_time
    return nil unless completed_at && processed_at
    completed_at - processed_at
  end
end