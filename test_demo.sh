#!/bin/bash

###############################################################################
# Shopify Analytics AI - Demo Test Script
# 
# This script tests all major features of the system to verify functionality
# Prerequisites: Both Rails API and Python AI Service must be running
###############################################################################

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RAILS_URL="http://localhost:3000"
PYTHON_URL="http://localhost:8000"
WAIT_TIME=3

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}► Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

wait_for_service() {
    echo -n "Waiting for service to respond..."
    sleep $WAIT_TIME
    echo " done"
}

test_endpoint() {
    local url=$1
    local description=$2
    
    print_test "$description"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" = "200" ]; then
        print_success "Endpoint responding (HTTP $response)"
    else
        print_error "Endpoint failed (HTTP $response)"
    fi
}

test_post_endpoint() {
    local url=$1
    local data=$2
    local description=$3
    
    print_test "$description"
    
    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    if echo "$response" | grep -q "success"; then
        print_success "Request successful"
        echo "$response" | jq . 2>/dev/null || echo "$response"
    else
        print_error "Request failed"
        echo "$response"
    fi
}

###############################################################################
# Main Test Suite
###############################################################################

print_header "SHOPIFY ANALYTICS AI - DEMO TEST SUITE"

echo -e "${BLUE}Configuration:${NC}"
echo "  Rails API: $RAILS_URL"
echo "  Python AI Service: $PYTHON_URL"
echo ""

###############################################################################
# Phase 1: Health Checks
###############################################################################

print_header "Phase 1: Service Health Checks"

# Test Rails API health
test_endpoint "$RAILS_URL/health" "Rails API health check"

# Test Python AI Service health
test_endpoint "$PYTHON_URL/health" "Python AI Service health check"

# Test Python AI Service root
test_endpoint "$PYTHON_URL/" "Python AI Service info endpoint"

wait_for_service

###############################################################################
# Phase 2: Inventory Forecasting
###############################################################################

print_header "Phase 2: Inventory Forecasting Tests"

# Test 1: Product-specific forecast
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "How many units of Blue T-Shirt will I need next month?"}' \
    "Product-specific inventory forecast"

wait_for_service

# Test 2: General reorder question
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "How much inventory should I reorder?"}' \
    "General inventory reorder recommendation"

wait_for_service

###############################################################################
# Phase 3: Inventory Status
###############################################################################

print_header "Phase 3: Inventory Status Tests"

# Test 3: Low stock alert
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "Which products will go out of stock in 7 days?"}' \
    "Low stock alert (7 days)"

wait_for_service

# Test 4: Current stock check
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "What is my current stock level for Black Jeans?"}' \
    "Current stock level check"

wait_for_service

###############################################################################
# Phase 4: Sales Analysis
###############################################################################

print_header "Phase 4: Sales Analysis Tests"

# Test 5: Top products
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "Top 5 selling products last week"}' \
    "Top 5 products ranking"

wait_for_service

# Test 6: Product performance
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "What were my best sellers in November?"}' \
    "Best sellers by month"

wait_for_service

###############################################################################
# Phase 5: Customer Analysis
###############################################################################

print_header "Phase 5: Customer Analysis Tests"

# Test 7: Repeat customers
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "Which customers placed repeat orders in last 90 days?"}' \
    "Repeat customers identification"

wait_for_service

# Test 8: Top customers
test_post_endpoint "$RAILS_URL/api/v1/questions" \
    '{"question": "Who are my top 5 customers by order count?"}' \
    "Top customers by order count"

wait_for_service

###############################################################################
# Phase 6: Query History
###############################################################################

print_header "Phase 6: Query History Tests"

# Test 9: List query history
print_test "Retrieve query history"
response=$(curl -s "$RAILS_URL/api/v1/questions")

if echo "$response" | grep -q "success"; then
    count=$(echo "$response" | jq '.data | length' 2>/dev/null)
    print_success "Retrieved query history ($count queries)"
else
    print_error "Failed to retrieve query history"
fi

wait_for_service

# Test 10: Get specific query
print_test "Retrieve specific query details"
response=$(curl -s "$RAILS_URL/api/v1/questions/1")

if echo "$response" | grep -q "success"; then
    print_success "Retrieved query details"
else
    print_error "Failed to retrieve query details"
fi

###############################################################################
# Phase 7: Edge Cases
###############################################################################

print_header "Phase 7: Edge Case Tests"

# Test 11: Empty question
print_test "Handle empty question"
response=$(curl -s -X POST "$RAILS_URL/api/v1/questions" \
    -H "Content-Type: application/json" \
    -d '{"question": ""}')

if echo "$response" | grep -q "error\|Missing"; then
    print_success "Correctly rejected empty question"
else
    print_error "Failed to handle empty question"
fi

wait_for_service

# Test 12: Very long question
print_test "Handle very long question"
long_question="What are the top selling products in my store and can you also tell me about inventory levels and customer patterns and sales trends for the last year and forecast for next year"
response=$(curl -s -X POST "$RAILS_URL/api/v1/questions" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"$long_question\"}")

if echo "$response" | grep -q "success\|completed"; then
    print_success "Handled long question successfully"
else
    print_error "Failed to handle long question"
fi

###############################################################################
# Test Summary
###############################################################################

print_header "TEST SUMMARY"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}Total Tests: $TOTAL_TESTS${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! System is working correctly.${NC}\n"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Please check the output above.${NC}\n"
    exit 1
fi

###############################################################################
# Usage Instructions
###############################################################################

: <<'USAGE'
Usage: ./test_demo.sh

Prerequisites:
1. Rails API must be running on http://localhost:3000
   Start with: cd rails_api && rails s

2. Python AI Service must be running on http://localhost:8000
   Start with: cd ai_service && uvicorn main:app --reload --port 8000

3. Both services should be in DEMO_MODE=true

Example:
  chmod +x test_demo.sh
  ./test_demo.sh

USAGE