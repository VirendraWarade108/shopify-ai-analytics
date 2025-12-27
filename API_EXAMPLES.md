# API Examples

Complete examples of API requests and responses for all supported question types.

## Base URLs

- **Rails API**: `http://localhost:3000`
- **Python AI Service**: `http://localhost:8000`

## Authentication

In demo mode, no authentication is required. For production with real Shopify data:

1. Initiate OAuth: `GET /auth/shopify?shop=yourshop.myshopify.com`
2. Complete callback: Shopify redirects to `/auth/shopify/callback`
3. Use returned session for subsequent requests

## Inventory Forecasting

### Example 1: Product-Specific Forecast

**Request:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many units of Blue T-Shirt will I need next month?"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question": "How many units of Blue T-Shirt will I need next month?",
    "status": "completed",
    "intent": {
      "domain": "inventory_forecasting",
      "confidence": 0.92,
      "entities": {
        "product_name": "Blue T-Shirt",
        "time_period": "next month"
      },
      "time_range": "next_30_days",
      "requires_forecast": true
    },
    "insights": {
      "summary": "You'll need approximately 300 Blue T-Shirts next month",
      "key_findings": [
        "You sell about 8 Blue T-Shirts per day",
        "Based on 90 days of sales history",
        "Projected sales: 250 units",
        "Safety stock added: 50 units"
      ],
      "recommendations": [
        "Order 300 units of Blue T-Shirt to cover next month",
        "Monitor sales velocity weekly to adjust forecasts"
      ],
      "data_summary": {
        "total_rows": 90,
        "forecast_applied": true,
        "daily_velocity": 8.3
      }
    },
    "confidence": 0.88,
    "created_at": "2024-12-27T10:00:00Z"
  }
}
```

### Example 2: General Reorder Question

**Request:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much inventory should I reorder?"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "question": "How much inventory should I reorder?",
    "status": "completed",
    "intent": {
      "domain": "inventory_forecasting",
      "confidence": 0.85
    },
    "insights": {
      "summary": "Reorder recommendations for your top 3 products",
      "key_findings": [
        "Blue T-Shirt: Need 300 units (sells 8/day)",
        "Red Hoodie: Need 180 units (sells 5/day)",
        "Black Jeans: Need 400 units (sells 12/day)"
      ],
      "recommendations": [
        "Prioritize Black Jeans - highest velocity",
        "Total reorder: approximately 880 units across all products"
      ]
    },
    "confidence": 0.82
  }
}
```

## Inventory Status

### Example 3: Low Stock Alert

**Request:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which products will go out of stock in 7 days?"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "question": "Which products will go out of stock in 7 days?",
    "status": "completed",
    "intent": {
      "domain": "inventory_status",
      "confidence": 0.90
    },
    "insights": {
      "summary": "2 products will run out within 7 days",
      "key_findings": [
        "White Sneakers: 8 units left, runs out in 1 day",
        "Black Jeans: 15 units left, runs out in 1 day"
      ],
      "recommendations": [
        "URGENT: Reorder White Sneakers immediately",
        "URGENT: Reorder Black Jeans immediately",
        "Blue T-Shirt is safe with 6 days of stock remaining"
      ],
      "data_summary": {
        "critical_products": 2,
        "warning_products": 1
      }
    },
    "confidence": 0.92
  }
}
```

## Sales Analysis

### Example 4: Top Products

**Request:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 selling products last week"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 4,
    "question": "Top 5 selling products last week",
    "status": "completed",
    "intent": {
      "domain": "product_ranking",
      "confidence": 0.94
    },
    "insights": {
      "summary": "Your top 5 products sold 1,920 units last week",
      "key_findings": [
        "1st: Blue T-Shirt - 680 units ($13,600 revenue)",
        "2nd: Red Hoodie - 420 units ($16,800 revenue)",
        "3rd: Black Jeans - 350 units ($21,000 revenue)",
        "4th: White Sneakers - 290 units ($23,200 revenue)",
        "5th: Green Cap - 180 units ($3,600 revenue)"
      ],
      "recommendations": [
        "White Sneakers has highest revenue despite lower quantity",
        "Focus marketing on top 3 products for volume",
        "Consider bundling Green Cap with higher-value items"
      ],
      "data_summary": {
        "total_units": 1920,
        "total_revenue": 78200,
        "time_period": "last_7_days"
      }
    },
    "confidence": 0.91
  }
}
```

## Customer Analysis

### Example 5: Repeat Customers

**Request:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which customers placed repeat orders in last 90 days?"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "question": "Which customers placed repeat orders in last 90 days?",
    "status": "completed",
    "intent": {
      "domain": "customer_analysis",
      "confidence": 0.89
    },
    "insights": {
      "summary": "You have 4 repeat customers in the last 90 days",
      "key_findings": [
        "mike.brown@example.com: 7 orders, $620 spent",
        "john.smith@example.com: 5 orders, $450 spent",
        "emma.davis@example.com: 4 orders, $380 spent",
        "sarah.jones@example.com: 3 orders, $280 spent"
      ],
      "recommendations": [
        "Reward your top customer Mike Brown with loyalty discount",
        "Total repeat customer revenue: $1,730",
        "Consider email campaign targeting these customers"
      ],
      "data_summary": {
        "repeat_customers": 4,
        "total_orders": 19,
        "average_orders_per_customer": 4.75
      }
    },
    "confidence": 0.87
  }
}
```

## Query History

### Get All Queries

**Request:**
```bash
curl http://localhost:3000/api/v1/questions
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "question": "Which customers placed repeat orders in last 90 days?",
      "status": "completed",
      "confidence": 0.87,
      "created_at": "2024-12-27T10:15:00Z"
    },
    {
      "id": 4,
      "question": "Top 5 selling products last week",
      "status": "completed",
      "confidence": 0.91,
      "created_at": "2024-12-27T10:10:00Z"
    }
  ]
}
```

### Get Specific Query

**Request:**
```bash
curl http://localhost:3000/api/v1/questions/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question": "How many units of Blue T-Shirt will I need next month?",
    "status": "completed",
    "intent": { ... },
    "query": "FROM orders SHOW product_name, SUM(quantity) ...",
    "insights": { ... },
    "confidence": 0.88,
    "created_at": "2024-12-27T10:00:00Z",
    "updated_at": "2024-12-27T10:00:05Z"
  }
}
```

## Error Responses

### Invalid Question

**Request:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": ""}'
```

**Response:**
```json
{
  "success": false,
  "error": "Missing required parameter: question",
  "status": 400
}
```

### AI Service Unavailable

**Response:**
```json
{
  "success": false,
  "error": "Failed to process question",
  "errors": {
    "details": "Could not connect to AI service at http://localhost:8000"
  },
  "status": 503
}
```

## Direct Python API Usage

You can also call the Python service directly:

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 products last week",
    "shop_domain": "demo.myshopify.com",
    "access_token": "demo_token"
  }'
```

## Testing Script

Save as `test_api.sh`:
```bash
#!/bin/bash

BASE_URL="http://localhost:3000"

echo "Testing Inventory Forecasting..."
curl -X POST $BASE_URL/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "How many Blue T-Shirts will I need next month?"}'

echo -e "\n\nTesting Low Stock..."
curl -X POST $BASE_URL/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Which products will go out of stock in 7 days?"}'

echo -e "\n\nTesting Top Products..."
curl -X POST $BASE_URL/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 selling products last week"}'

echo -e "\n\nDone!"
```

Run