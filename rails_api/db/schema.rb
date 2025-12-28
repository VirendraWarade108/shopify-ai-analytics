# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 2024_12_27_000002) do
  create_table "analytics_queries", force: :cascade do |t|
    t.integer "shop_id", null: false
    t.text "question", null: false
    t.string "status", default: "pending", null: false
    t.json "intent"
    t.text "shopifyql_query"
    t.json "insights"
    t.decimal "confidence_score", precision: 5, scale: 4
    t.json "response_data"
    t.text "error_message"
    t.datetime "completed_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["completed_at"], name: "index_analytics_queries_on_completed_at"
    t.index ["confidence_score"], name: "index_analytics_queries_on_confidence_score"
    t.index ["created_at"], name: "index_analytics_queries_on_created_at"
    t.index ["shop_id", "created_at"], name: "index_queries_on_shop_and_created_at"
    t.index ["shop_id", "status"], name: "index_queries_on_shop_and_status"
    t.index ["shop_id"], name: "index_analytics_queries_on_shop_id"
    t.index ["status"], name: "index_analytics_queries_on_status"
  end

  create_table "shops", force: :cascade do |t|
    t.string "shopify_domain", null: false
    t.text "shopify_token_ciphertext"
    t.boolean "active", default: true, null: false
    t.string "shop_name"
    t.string "shop_email"
    t.string "shop_owner"
    t.string "plan_name"
    t.string "country_code"
    t.string "currency"
    t.datetime "installed_at"
    t.datetime "uninstalled_at"
    t.datetime "last_authenticated_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["active"], name: "index_shops_on_active"
    t.index ["created_at"], name: "index_shops_on_created_at"
    t.index ["installed_at"], name: "index_shops_on_installed_at"
    t.index ["shopify_domain"], name: "index_shops_on_shopify_domain", unique: true
  end

  add_foreign_key "analytics_queries", "shops"
end
