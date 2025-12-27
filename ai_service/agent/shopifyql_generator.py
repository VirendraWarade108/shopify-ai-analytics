"""
ShopifyQL Generator
Stage 3: Generates Shopify Analytics queries
"""

import structlog
from typing import Dict, Any
from anthropic import Anthropic

logger = structlog.get_logger()


class ShopifyQLGenerator:
    """
    Generates ShopifyQL queries based on intent and plan
    
    ShopifyQL is Shopify's analytics query language, similar to SQL
    Example: FROM orders SHOW total_sales, order_count BY month WHERE created_at >= '2024-01-01'
    """
    
    def __init__(self, api_key: str, model: str):
        """Initialize the ShopifyQL generator"""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info("shopifyql_generator_initialized")
    
    async def generate(
        self,
        question: str,
        intent: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> str:
        """
        Generate a ShopifyQL query
        
        Args:
            question: Original natural language question
            intent: Classified intent
            plan: Query execution plan
            
        Returns:
            ShopifyQL query string
        """
        logger.info("generating_shopifyql",
                   question=question[:100],
                   data_sources=plan.get("data_sources"))
        
        prompt = self._build_prompt(question, intent, plan)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse and clean query
            query = self._parse_response(response.content[0].text)
            
            logger.info("shopifyql_generated", query=query[:100])
            
            return query
            
        except Exception as e:
            logger.error("shopifyql_generation_failed",
                        error=str(e),
                        exc_info=True)
            
            # Return default query
            return self._get_default_query(plan)
    
    def _build_prompt(
        self,
        question: str,
        intent: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> str:
        """Build the ShopifyQL generation prompt"""
        return f"""Generate a ShopifyQL query for this analytics question.

Question: "{question}"

Intent:
- Domain: {intent.get('domain')}
- Entities: {intent.get('entities')}

Query Plan:
- Data Sources: {plan.get('data_sources')}
- Primary Metric: {plan.get('primary_metric')}
- Aggregations: {plan.get('aggregations')}
- Filters: {plan.get('filters')}
- Group By: {plan.get('group_by')}

ShopifyQL Syntax Examples:
1. FROM orders SHOW total_sales, order_count BY month WHERE created_at >= '2024-01-01'
2. FROM products SHOW product_name, inventory_quantity WHERE inventory_quantity < 10
3. FROM orders SHOW product_name, SUM(quantity) AS total_quantity GROUP BY product_name ORDER BY total_quantity DESC LIMIT 5
4. FROM customers SHOW customer_email, COUNT(order_id) AS order_count WHERE created_at >= '2024-01-01' GROUP BY customer_email HAVING order_count > 1

Available fields by data source:

**orders:**
- created_at, order_id, total_price, subtotal_price
- product_name, product_id, quantity, line_item_price
- customer_email, customer_id

**products:**
- product_id, product_name, product_type, vendor
- inventory_quantity, price, sku

**customers:**
- customer_id, customer_email, customer_name
- total_spent, order_count, created_at

Rules:
1. Use proper ShopifyQL syntax
2. Include WHERE clauses for date filters
3. Use GROUP BY for aggregations
4. Use ORDER BY and LIMIT for rankings
5. Reference only fields that exist in the schema above

Respond ONLY with the ShopifyQL query, no explanations or markdown.

Generate the query now:"""
    
    def _parse_response(self, response_text: str) -> str:
        """Parse and clean the ShopifyQL query"""
        # Clean response
        query = response_text.strip()
        
        # Remove markdown code blocks if present
        if query.startswith("```"):
            lines = query.split("\n")
            query = "\n".join(lines[1:-1]) if len(lines) > 2 else query
        
        query = query.replace("```sql", "").replace("```", "").strip()
        
        # Remove any explanatory text before the query
        if "\n\n" in query:
            parts = query.split("\n\n")
            # Take the part that starts with FROM
            for part in parts:
                if part.strip().upper().startswith("FROM"):
                    query = part.strip()
                    break
        
        # Ensure query starts with FROM
        if not query.upper().startswith("FROM"):
            logger.warning("invalid_query_format", query=query[:100])
            # Try to find FROM clause
            if "FROM" in query.upper():
                idx = query.upper().index("FROM")
                query = query[idx:]
        
        return query
    
    def _get_default_query(self, plan: Dict[str, Any]) -> str:
        """Get default query based on plan"""
        data_source = plan.get("data_sources", ["orders"])[0]
        metric = plan.get("primary_metric", "quantity_sold")
        filters = plan.get("filters", {})
        
        # Build basic query
        if data_source == "orders":
            query = "FROM orders SHOW product_name, SUM(quantity) AS total_quantity"
            
            if filters.get("date_range"):
                query += " WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            
            if "product_name" in plan.get("group_by", []):
                query += " GROUP BY product_name ORDER BY total_quantity DESC"
            
            query += " LIMIT 10"
            
        elif data_source == "products":
            query = "FROM products SHOW product_name, inventory_quantity WHERE inventory_quantity < 50"
            
        else:
            query = "FROM customers SHOW customer_email, COUNT(order_id) AS order_count GROUP BY customer_email HAVING order_count > 1"
        
        return query