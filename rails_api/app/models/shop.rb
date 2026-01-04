class Shop < ApplicationRecord
  # Validations
  validates :shopify_domain, presence: true, uniqueness: true
  
  # The database column is 'shopify_token_ciphertext' because it was created for encryption
  # For demo mode, we'll create a virtual attribute 'shopify_token' that maps to the ciphertext column
  
  # Virtual attribute for shopify_token
  def shopify_token
    shopify_token_ciphertext
  end
  
  def shopify_token=(value)
    self.shopify_token_ciphertext = value
  end
  
  # Validations
  validates :shopify_token_ciphertext, presence: true
  
  # Associations
  has_many :questions, dependent: :destroy
  
  # Scopes
  scope :active, -> { where(active: true) }
  
  # Instance methods
  def display_name
    shopify_domain.split('.').first.titleize
  end
  
  def active?
    active == true
  end
end
