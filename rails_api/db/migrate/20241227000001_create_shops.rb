class CreateShops < ActiveRecord::Migration[7.1]
  def change
    create_table :shops do |t|
      # Core Shopify identification
      t.string :shopify_domain, null: false, index: { unique: true }
      
      # Encrypted access token (using Lockbox)
      t.text :shopify_token_ciphertext
      
      # Shop status
      t.boolean :active, default: true, null: false
      
      # Additional metadata
      t.string :shop_name
      t.string :shop_email
      t.string :shop_owner
      t.string :plan_name
      t.string :country_code
      t.string :currency
      
      # Timestamps for tracking
      t.datetime :installed_at
      t.datetime :uninstalled_at
      t.datetime :last_authenticated_at
      
      # Standard timestamps
      t.timestamps
    end

    # Indexes for common queries
    add_index :shops, :active
    add_index :shops, :created_at
    add_index :shops, :installed_at
  end
end