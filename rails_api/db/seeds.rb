# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).

# Example:
#
#   movies = Movie.create([{ name: "Star Wars" }, { name: "Lord of the Rings" }])
#   Character.create(name: "Luke", movie: movies.first)

# Seed data for Shopify Analytics AI

puts "Starting database seed..."

# Create demo shop if it doesn't exist
demo_shop = Shop.find_or_create_by(shopify_domain: 'demo.myshopify.com') do |shop|
  shop.shopify_token = 'demo_token'
  shop.shop_name = 'Demo Store'
  shop.active = true
  shop.installed_at = Time.current
  puts "  ✓ Created demo shop"
end

# Create some sample queries for demo purposes
sample_questions = [
  "How many units of Blue T-Shirt will I need next month?",
  "Which products will go out of stock in 7 days?",
  "Top 5 selling products last week",
  "Which customers placed repeat orders in last 90 days?",
  "What is my current inventory status?"
]

sample_questions.each do |question|
  unless demo_shop.analytics_queries.exists?(question: question)
    demo_shop.analytics_queries.create!(
      question: question,
      status: 'pending'
    )
  end
end

puts "  ✓ Created #{sample_questions.count} sample queries"

puts "\nSeed completed successfully!"
puts "Demo shop: #{demo_shop.shopify_domain}"
puts "Sample queries: #{demo_shop.analytics_queries.count}"