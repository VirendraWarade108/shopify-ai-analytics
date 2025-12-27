"""
Query Planner
Stage 2: Determines data sources and aggregations needed
"""

import structlog
from typing import Dict, Any
from anthropic import Anthropic

logger = structlog.get_logger()


class QueryPlanner:
    """
    Plans the data retrieval strategy for a query
    
    Determines:
    - Which Shopify data sources to query (orders, products, customers)
    - What aggregations to perform (sum, count, average)
    - What filters to apply (date ranges, product IDs)
    - Whether forecasting is needed
    """
    
    def __init__(self, api_key: str, model: str):
        """Initialize the query planner"""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info("query_planner_initialized")
    
    async def plan(self, question: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a query execution plan
        
        Args:
            question: Natural language question
            intent: Classified intent from Stage 1
            
        Returns:
            Query plan with data sources and operations
        """
        logger.info("planning_query",
                   question=question[:100],
                   intent_domain=intent.get("domain"))
        
        prompt = self._build_prompt(question, intent)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            plan = self._parse_response(response.content[0].text)
            
            logger.info("query_planned",
                       data_sources=plan.get("data_sources"),
                       requires_forecast=plan.get("requires_forecast"))
            
            return plan
            
        except Exception as e:
            logger.error("query_planning_failed",
                        error=str(e),
                        exc_info=True)
            
            # Return default plan
            return self._get_default_plan(intent)
    
    def _build_prompt(self, question: str, intent: Dict[str, Any]) -> str:
        """Build the planning prompt"""
        return f"""Create a data retrieval plan for this analytics question.

Question: "{question}"

Intent Classification:
- Domain: {intent.get('domain')}
- Entities: {intent.get('entities')}
- Time Range: {intent.get('time_range')}
- Requires Forecast: {intent.get('requires_forecast')}

Available Shopify data sources:
1. orders - Order transactions (date, total, product, quantity)
2. products - Product catalog (name, SKU, price, inventory)
3. customers - Customer information (email, orders, lifetime value)

Respond ONLY with a JSON object in this exact format:
{{
  "data_sources": ["orders", "products"],
  "primary_metric": "quantity_sold",
  "aggregations": ["sum", "daily_average"],
  "filters": {{
    "date_range": "last_90_days",
    "product_name": "Blue T-Shirt"
  }},
  "requires_forecast": true,
  "forecast_config": {{
    "method": "linear_regression",
    "historical_days": 90,
    "forecast_days": 30
  }},
  "group_by": ["product_name", "date"]
}}

Create the plan now:"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into plan object"""
        import json
        
        # Clean response
        response_text = response_text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            plan = json.loads(response_text)
            
            # Set defaults
            plan.setdefault("data_sources", ["orders"])
            plan.setdefault("primary_metric", "quantity_sold")
            plan.setdefault("aggregations", ["sum"])
            plan.setdefault("filters", {})
            plan.setdefault("requires_forecast", False)
            plan.setdefault("group_by", [])
            
            # Add forecast config if needed
            if plan.get("requires_forecast") and "forecast_config" not in plan:
                plan["forecast_config"] = {
                    "method": "linear_regression",
                    "historical_days": 90,
                    "forecast_days": 30
                }
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error("plan_parse_error",
                        error=str(e),
                        response=response_text[:200])
            
            # Return safe default
        return {
            "data_sources": ["orders"],
            "primary_metric": "quantity_sold",
            "aggregations": ["sum"],
            "filters": {"date_range": "last_30_days"},
            "requires_forecast": False,
            "group_by": []
        }

def _get_default_plan(self, intent: Dict[str, Any]) -> Dict[str, Any]:
    """Get default plan based on intent domain"""
    domain = intent.get("domain", "sales_analysis")
    
    plans = {
        "inventory_forecasting": {
            "data_sources": ["orders", "products"],
            "primary_metric": "quantity_sold",
            "aggregations": ["sum", "daily_average"],
            "filters": {"date_range": "last_90_days"},
            "requires_forecast": True,
            "forecast_config": {
                "method": "linear_regression",
                "historical_days": 90,
                "forecast_days": 30
            },
            "group_by": ["product_name"]
        },
        "sales_analysis": {
            "data_sources": ["orders"],
            "primary_metric": "quantity_sold",
            "aggregations": ["sum", "count"],
            "filters": {"date_range": "last_30_days"},
            "requires_forecast": False,
            "group_by": ["product_name"]
        },
        "customer_analysis": {
            "data_sources": ["customers", "orders"],
            "primary_metric": "order_count",
            "aggregations": ["count", "sum"],
            "filters": {"date_range": "last_90_days"},
            "requires_forecast": False,
            "group_by": ["customer_email"]
        }
    }
    
    return plans.get(domain, plans["sales_analysis"])