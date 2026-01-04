"""
Agent Orchestrator - FREE MOCK MODE
No API calls, generates synthetic responses
"""

import structlog
from typing import Dict, Any, Optional
import re

logger = structlog.get_logger()


class AgentOrchestrator:
    """
    Orchestrates the 5-stage agent pipeline with FREE mock mode
    No external API calls - everything runs locally
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """Initialize in mock mode"""
        self.api_key = api_key
        self.model = model
        logger.info("orchestrator_initialized", model="MOCK_MODE", mock=True)
    
    async def process_query(
        self,
        question: str,
        shop_domain: str,
        access_token: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query using mock responses (100% FREE)
        """
        logger.info("pipeline_started_mock", question=question[:100])
        
        try:
            # Stage 1: Mock Intent Classification
            intent = self._mock_intent_classification(question)
            logger.info("stage_1_completed_mock", domain=intent.get("domain"))
            
            # Stage 2: Mock Query Planning
            plan = self._mock_query_planning(intent)
            logger.info("stage_2_completed_mock")
            
            # Stage 3: Mock ShopifyQL Generation
            query = self._mock_shopifyql_generation(intent, plan)
            logger.info("stage_3_completed_mock")
            
            # Stage 4: Generate Synthetic Data
            execution_result = self._generate_synthetic_data(plan)
            logger.info("stage_4_completed_mock", data_points=len(execution_result.get("data", [])))
            
            # Stage 5: Mock Insight Synthesis
            insights = self._mock_insight_synthesis(question, intent, execution_result)
            logger.info("stage_5_completed_mock")
            
            # Calculate confidence
            confidence = 0.85
            
            response = {
                "status": "completed",
                "intent": intent,
                "query": query,
                "insights": insights,
                "confidence": confidence,
                "metadata": {
                    "shop_domain": shop_domain,
                    "data_points": len(execution_result.get("data", [])),
                    "forecast_applied": execution_result.get("forecast_applied", False),
                    "mock_mode": True
                }
            }
            
            logger.info("pipeline_completed_mock", status="success")
            return response
            
        except Exception as e:
            logger.error("pipeline_failed_mock", error=str(e), exc_info=True)
            return {
                "status": "failed",
                "intent": {},
                "query": "",
                "insights": {
                    "summary": "Failed to process query",
                    "key_findings": [],
                    "recommendations": []
                },
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _mock_intent_classification(self, question: str) -> Dict[str, Any]:
        """Mock AI intent classification"""
        question_lower = question.lower()
        
        # Detect intent from keywords
        if any(word in question_lower for word in ["forecast", "need", "reorder", "next month", "next week"]):
            domain = "inventory_forecasting"
            requires_forecast = True
        elif any(word in question_lower for word in ["stock", "out of stock", "inventory", "available"]):
            domain = "inventory_status"
            requires_forecast = False
        elif any(word in question_lower for word in ["customer", "repeat", "loyal"]):
            domain = "customer_analysis"
            requires_forecast = False
        elif any(word in question_lower for word in ["top", "best", "worst", "rank"]):
            domain = "product_ranking"
            requires_forecast = False
        else:
            domain = "sales_analysis"
            requires_forecast = False
        
        # Extract product name
        product_match = re.search(r'(blue t-shirt|red hoodie|black jeans|white sneakers|green cap)', question_lower)
        product_name = product_match.group(1).title() if product_match else None
        
        # Extract time period
        time_match = re.search(r'(last|next) (\d+) (day|week|month)', question_lower)
        time_period = time_match.group(0) if time_match else "last 30 days"
        
        return {
            "domain": domain,
            "confidence": 0.92,
            "entities": {
                "product_name": product_name,
                "time_period": time_period
            } if product_name or time_period else {},
            "time_range": "next_30_days" if requires_forecast else "last_30_days",
            "requires_forecast": requires_forecast
        }
    
    def _mock_query_planning(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Mock query planning"""
        domain = intent.get("domain", "sales_analysis")
        
        plans = {
            "inventory_forecasting": {
                "data_sources": ["orders", "products"],
                "primary_metric": "quantity_sold",
                "aggregations": ["sum", "average"],
                "requires_forecast": True,
                "forecast_config": {
                    "method": "linear_regression",
                    "forecast_days": 30,
                    "historical_days": 90
                }
            },
            "sales_analysis": {
                "data_sources": ["orders"],
                "primary_metric": "quantity_sold",
                "aggregations": ["sum", "count"],
                "requires_forecast": False
            },
            "customer_analysis": {
                "data_sources": ["customers", "orders"],
                "primary_metric": "order_count",
                "aggregations": ["count"],
                "requires_forecast": False
            }
        }
        
        return plans.get(domain, plans["sales_analysis"])
    
    def _mock_shopifyql_generation(self, intent: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """Mock ShopifyQL generation"""
        domain = intent.get("domain")
        
        if domain == "inventory_forecasting":
            return "FROM orders SHOW product_name, SUM(quantity) AS total_quantity GROUP BY product_name WHERE created_at >= '2024-10-01'"
        elif domain == "product_ranking":
            return "FROM orders SHOW product_name, SUM(quantity) AS total_quantity GROUP BY product_name ORDER BY total_quantity DESC LIMIT 5"
        elif domain == "customer_analysis":
            return "FROM customers SHOW email, COUNT(order_id) AS order_count GROUP BY email HAVING order_count > 1"
        else:
            return "FROM orders SHOW product_name, SUM(quantity) AS total_quantity GROUP BY product_name"
    
    def _generate_synthetic_data(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic synthetic data"""
        import random
        
        products = [
            {"name": "Blue T-Shirt", "base_quantity": 680, "velocity": 8.3},
            {"name": "Red Hoodie", "base_quantity": 420, "velocity": 5.2},
            {"name": "Black Jeans", "base_quantity": 350, "velocity": 12.1},
            {"name": "White Sneakers", "base_quantity": 290, "velocity": 9.8},
            {"name": "Green Cap", "base_quantity": 180, "velocity": 3.5}
        ]
        
        data = []
        for product in products:
            row = {
                "product_name": product["name"],
                "quantity": product["base_quantity"] + random.randint(-50, 50),
                "revenue": (product["base_quantity"] + random.randint(-50, 50)) * random.uniform(20, 80)
            }
            
            # Add forecast if needed
            if plan.get("requires_forecast"):
                forecast_days = plan.get("forecast_config", {}).get("forecast_days", 30)
                daily_velocity = product["velocity"]
                forecast_quantity = int(daily_velocity * forecast_days)
                safety_stock = int(forecast_quantity * 0.2)
                
                row["forecast"] = {
                    "daily_velocity": daily_velocity,
                    "forecast_quantity": forecast_quantity,
                    "safety_stock": safety_stock,
                    "total_needed": forecast_quantity + safety_stock,
                    "forecast_days": forecast_days,
                    "confidence": 0.88
                }
            
            data.append(row)
        
        return {
            "data": data,
            "forecast_applied": plan.get("requires_forecast", False),
            "row_count": len(data)
        }
    
    def _mock_insight_synthesis(
        self,
        question: str,
        intent: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate business-friendly insights"""
        data = execution_result.get("data", [])
        domain = intent.get("domain")
        
        if not data:
            return {
                "summary": "No data found for this query",
                "key_findings": ["No matching data in your store"],
                "recommendations": ["Try adjusting your search criteria"],
                "data_summary": {"total_rows": 0}
            }
        
        # Generate insights based on domain
        if domain == "inventory_forecasting":
            product = data[0]
            forecast = product.get("forecast", {})
            return {
                "summary": f"You'll need approximately {int(forecast.get('total_needed', 0))} units of {product['product_name']} next month",
                "key_findings": [
                    f"You sell about {int(forecast.get('daily_velocity', 0))} {product['product_name']}s per day",
                    f"Based on 90 days of sales history",
                    f"Projected sales: {int(forecast.get('forecast_quantity', 0))} units",
                    f"Safety stock added: {int(forecast.get('safety_stock', 0))} units"
                ],
                "recommendations": [
                    f"Order {int(forecast.get('total_needed', 0))} units to cover next month",
                    "Monitor sales velocity weekly to adjust forecasts"
                ],
                "data_summary": {
                    "total_rows": len(data),
                    "forecast_applied": True
                }
            }
        
        elif domain == "product_ranking":
            top_product = data[0]
            total_quantity = sum(p.get("quantity", 0) for p in data)
            return {
                "summary": f"Your top 5 products sold {int(total_quantity)} units last week",
                "key_findings": [
                    f"{i+1}. {p['product_name']} - {int(p['quantity'])} units (${int(p['revenue']):,} revenue)"
                    for i, p in enumerate(data[:5])
                ],
                "recommendations": [
                    f"{data[0]['product_name']} is your best seller - ensure adequate stock",
                    "Focus marketing efforts on top 3 products",
                    f"Consider promotions for {data[-1]['product_name']} to boost sales"
                ],
                "data_summary": {
                    "total_rows": len(data),
                    "total_units": int(total_quantity),
                    "total_revenue": int(sum(p.get("revenue", 0) for p in data))
                }
            }
        
        else:  # sales_analysis
            total_quantity = sum(p.get("quantity", 0) for p in data)
            return {
                "summary": f"Found {len(data)} products with {int(total_quantity)} total units sold",
                "key_findings": [
                    f"{p['product_name']}: {int(p['quantity'])} units sold"
                    for p in data[:3]
                ],
                "recommendations": [
                    "Review top performers for restocking priorities",
                    "Consider bundling popular items"
                ],
                "data_summary": {
                    "total_rows": len(data),
                    "total_units": int(total_quantity)
                }
            }