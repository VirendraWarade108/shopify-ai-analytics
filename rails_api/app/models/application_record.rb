class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  # Common scopes
  scope :recent, -> { order(created_at: :desc) }
  scope :active, -> { where(active: true) }

  # Utility methods available to all models
  def to_json_api
    as_json(except: [:created_at, :updated_at])
  end

  # Log model changes
  after_create :log_creation
  after_update :log_update
  after_destroy :log_destruction

  private

  def log_creation
    Rails.logger.info({
      event: 'record_created',
      model: self.class.name,
      id: id,
      attributes: changes
    }.to_json)
  end

  def log_update
    return unless saved_changes.any?
    
    Rails.logger.info({
      event: 'record_updated',
      model: self.class.name,
      id: id,
      changes: saved_changes
    }.to_json)
  end

  def log_destruction
    Rails.logger.info({
      event: 'record_destroyed',
      model: self.class.name,
      id: id
    }.to_json)
  end
end