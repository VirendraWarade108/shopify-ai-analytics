"""
Insight Synthesizer
Stage 5: Transforms data into business-friendly insights
"""

import structlog
from typing import Dict, Any, List
from anthropic import Anthropic

logger = structlog.get_logger()


class InsightSynthesizer:
    """
    Synthesizes raw query results into business-friendly insights
    
    Transforms technical data and forecasts into:
    - Clear summary statements
    - Key findings in plain language
    - Actionable recommendations
    """
    
    def __init__(self, api_key: str, model: str):
        """Initialize the insight synthesizer"""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info("insight_synthesizer_initialized")
    
    async def synthesize(
        self,
        question: str,
        intent: Dict[str, Any],
        plan: Dict[str, Any],
        query: str,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize insights from query results
        
        Args:
            question: Original question
            intent: Classified intent
            plan: Query plan
            query: ShopifyQL query
            execution_result: Query execution results
            
        Returns:
            Insights object with summary, findings, and recommendations
        """
        logger.info("synthesizing_insights",
                   question=question[:100],
                   data_points=len(execution_result.get("data", [])))
        
        data = execution_result.get("data", [])
        
        if not data:
            return self._generate_empty_insights(question)
        
        prompt = self._build_prompt(question, intent, data, execution_result)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            insights = self._parse_response(response.content[0].text, data)
            
            logger.info("insights_synthesized",
                       findings_count=len(insights.get("key_findings", [])))
            
            return insights
            
        except Exception as e:
            logger.error("insight_synthesis_failed",
                        error=str(e),
                        exc_info=True)
            
            # Return basic insights from data
            return self._generate_fallback_insights(question, data, execution_result)
    
    def _build_prompt(
        self,
        question: str,
        intent: Dict[str, Any],
        data: List[Dict[str, Any]],
        execution_result: Dict[str, Any]
    ) -> str:
        """Build the insight synthesis prompt"""
        # Format data for readability
        data_summary = self._summarize_data(data)
        forecast_info = self._extract_forecast_info(data)
        
        return f"""Transform this analytics data into business-friendly insights.

Original Question: "{question}"

Intent Domain: {intent.get('domain')}

Data Summary:
{data_summary}

Forecast Information:
{forecast_info if forecast_info else "No forecasting applied"}

Your task: Create insights that a store owner can immediately understand and act on.

CRITICAL RULES FOR BUSINESS-FRIENDLY LANGUAGE:
❌ BAD: "Average daily velocity is 8.3 units/day with coefficient 0.95"
✅ GOOD: "You sell about 8 Blue T-Shirts per day"

❌ BAD: "Aggregated forecast: 250 units + 20% buffer = 300"
✅ GOOD: "You'll need approximately 300 units next month (250 projected + 50 safety stock)"

❌ BAD: "Inventory depletion in 5.6 days based on current velocity"
✅ GOOD: "You'll run out of White Sneakers in about 6 days at your current sales pace"

Guidelines:
- Use everyday language, not technical jargon
- Round numbers to be human-readable (8.3 → "about 8")
- Explain calculations in simple terms
- Focus on actionable outcomes
- Use "you" to address the store owner directly

Respond ONLY with a JSON object in this exact format:
{{
  "summary": "One clear sentence answering the question",
  "key_findings": [
    "First key finding in plain language",
    "Second key finding",
    "Third key finding"
  ],
  "recommendations": [
    "First actionable recommendation",
    "Second actionable recommendation"
  ],
  "data_summary": {{
    "total_products": 5,
    "date_range": "last 7 days",
    "key_metric": "units sold"
  }}
}}

Generate the insights now:"""
    
    def _summarize_data(self, data: List[Dict[str, Any]]) -> str:
        """Create a readable summary of the data"""
        if not data:
            return "No data available"
        
        lines = []
        
        # Show first 5 rows
        for i, row in enumerate(data[:5]):
            if "product_name" in row:
                product = row["product_name"]
                
                if "forecast" in row:
                    forecast = row["forecast"]
                    lines.append(
                        f"- {product}: Daily velocity {forecast.get('daily_velocity')} units, "
                        f"need {forecast.get('total_needed')} units for next {forecast.get('forecast_days')} days"
                    )
                elif "quantity" in row:
                    lines.append(f"- {product}: {row['quantity']} units sold")
                elif "inventory_quantity" in row:
                    lines.append(f"- {product}: {row['inventory_quantity']} units in stock")
                elif "orders" in row:
                    lines.append(f"- Customer {row.get('email', 'unknown')}: {row['orders']} orders")
        
        if len(data) > 5:
            lines.append(f"... and {len(data) - 5} more rows")
        
        return "\n".join(lines) if lines else str(data[:3])
    
    def _extract_forecast_info(self, data: List[Dict[str, Any]]) -> str:
        """Extract forecast information from data"""
        forecast_rows = [row for row in data if "forecast" in row]
        
        if not forecast_rows:
            return ""
        
        lines = ["Forecasting applied:"]
        for row in forecast_rows[:3]:
            forecast = row["forecast"]
            product = row.get("product_name", "Unknown")
            lines.append(
                f"- {product}: {forecast.get('total_needed')} units needed "
                f"({forecast.get('forecast_quantity')} projected + "
                f"{forecast.get('safety_stock')} safety stock)"
            )
        
        return "\n".join(lines)
    
    def _parse_response(self, response_text: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse Claude's response into insights object"""
        import json
        
        # Clean response
        response_text = response_text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            insights = json.loads(response_text)
            
            # Ensure required fields
            insights.setdefault("summary", "Analysis completed")
            insights.setdefault("key_findings", [])
            insights.setdefault("recommendations", [])
            insights.setdefault("data_summary", {})
            
            # Add metadata
            insights["data_summary"]["total_rows"] = len(data)
            
            return insights
            
        except json.JSONDecodeError as e:
            logger.error("insights_parse_error",
                        error=str(e),
                        response=response_text[:200])
            
            # Return fallback
            return self._generate_fallback_insights("", data, {})
    
    def _generate_empty_insights(self, question: str) -> Dict[str, Any]:
        """Generate insights when no data is available"""
        return {
            "summary": "No data found for this query",
            "key_findings": [
                "No matching data was found in your store",
                "Try adjusting the time range or product filters"
            ],
            "recommendations": [
                "Check if the product name is spelled correctly",
                "Try expanding the date range for your query"
            ],
            "data_summary": {
                "total_rows": 0,
                "status": "no_data"
            }
        }
    
    def _generate_fallback_insights(
        self,
        question: str,
        data: List[Dict[str, Any]],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic insights when AI synthesis fails"""
        findings = []
        recommendations = []
        
        if not data:
            return self._generate_empty_insights(question)
        
        # Analyze data to extract basic insights
        if "forecast" in data[0]:
            # Forecast insights
            for row in data[:3]:
                product = row.get("product_name", "Unknown")
                forecast = row.get("forecast", {})
                total_needed = forecast.get("total_needed", 0)
                daily_velocity = forecast.get("daily_velocity", 0)
                
                findings.append(
                    f"You sell about {int(daily_velocity)} {product}s per day"
                )
                recommendations.append(
                    f"Order approximately {int(total_needed)} units of {product} for next month"
                )
        
        elif "inventory_quantity" in data[0]:
            # Inventory insights
            low_stock = [row for row in data if row.get("inventory_quantity", 0) < 50]
            if low_stock:
                findings.append(f"{len(low_stock)} products have low inventory")
                for row in low_stock[:2]:
                    product = row.get("product_name", "Unknown")
                    qty = row.get("inventory_quantity", 0)
                    findings.append(f"{product} has only {qty} units in stock")
        
        elif "quantity" in data[0]:
            # Sales insights
            total_quantity = sum(row.get("quantity", 0) for row in data)
            findings.append(f"Total of {int(total_quantity)} units sold")
            
            if len(data) > 0:
                top_product = data[0].get("product_name", "Unknown")
                top_quantity = data[0].get("quantity", 0)
                findings.append(f"{top_product} is your top seller with {int(top_quantity)} units")
        
        return {
            "summary": f"Found {len(data)} results for your query",
            "key_findings": findings if findings else ["Data retrieved successfully"],
            "recommendations": recommendations if recommendations else ["Review the data to identify trends"],
            "data_summary": {
                "total_rows": len(data),
                "forecast_applied": execution_result.get("forecast_applied", False)
            }
        }