class CreateAnalyticsQueries < ActiveRecord::Migration[7.1]
  def change
    create_table :analytics_queries do |t|
      # Association
      t.references :shop, null: false, foreign_key: true, index: true
      
      # Query information
      t.text :question, null: false
      t.string :status, null: false, default: 'pending'
      
      # AI processing results
      t.json :intent
      t.text :shopifyql_query
      t.json :insights
      t.decimal :confidence_score, precision: 5, scale: 4
      
      # Full response data for debugging/analysis
      t.json :response_data
      
      # Error handling
      t.text :error_message
      
      # Timing
      t.datetime :completed_at
      
      # Standard timestamps
      t.timestamps
    end

    # Indexes for common queries
    add_index :analytics_queries, :status
    add_index :analytics_queries, :created_at
    add_index :analytics_queries, :completed_at
    add_index :analytics_queries, :confidence_score
    add_index :analytics_queries, [:shop_id, :created_at], name: 'index_queries_on_shop_and_created_at'
    add_index :analytics_queries, [:shop_id, :status], name: 'index_queries_on_shop_and_status'
  end
end