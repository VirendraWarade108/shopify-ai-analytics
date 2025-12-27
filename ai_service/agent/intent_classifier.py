"""
Intent Classifier
Stage 1: Classifies user questions into structured intents
"""

import structlog
from typing import Dict, Any
from anthropic import Anthropic

logger = structlog.get_logger()


class IntentClassifier:
    """
    Classifies natural language questions into structured intents
    
    Intent domains:
    - inventory_forecasting: Questions about future inventory needs
    - inventory_status: Current stock status and availability
    - sales_analysis: Product sales performance
    - customer_analysis: Customer behavior and repeat purchases
    - product_ranking: Top/bottom performing products
    """
    
    INTENT_DOMAINS = [
        "inventory_forecasting",
        "inventory_status",
        "sales_analysis",
        "customer_analysis",
        "product_ranking"
    ]
    
    def __init__(self, api_key: str, model: str):
        """Initialize the intent classifier"""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info("intent_classifier_initialized")
    
    async def classify(self, question: str) -> Dict[str, Any]:
        """
        Classify a question into a structured intent
        
        Args:
            question: Natural language question
            
        Returns:
            Intent object with domain, confidence, and parameters
        """
        logger.info("classifying_intent", question=question[:100])
        
        prompt = self._build_prompt(question)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            intent = self._parse_response(response.content[0].text)
            
            logger.info("intent_classified",
                       domain=intent.get("domain"),
                       confidence=intent.get("confidence"))
            
            return intent
            
        except Exception as e:
            logger.error("intent_classification_failed",
                        error=str(e),
                        exc_info=True)
            
            # Return default intent on failure
            return {
                "domain": "sales_analysis",
                "confidence": 0.3,
                "entities": {},
                "time_range": "last_30_days",
                "requires_forecast": False
            }
    
    def _build_prompt(self, question: str) -> str:
        """Build the classification prompt"""
        return f"""Analyze this e-commerce analytics question and classify its intent.

Question: "{question}"

Available intent domains:
1. inventory_forecasting - Future inventory needs, reorder quantities, stock planning
2. inventory_status - Current stock levels, out-of-stock items, availability
3. sales_analysis - Product sales performance, revenue, conversion
4. customer_analysis - Customer behavior, repeat purchases, loyalty
5. product_ranking - Top/bottom products, comparisons, rankings

Respond ONLY with a JSON object in this exact format:
{{
  "domain": "inventory_forecasting",
  "confidence": 0.92,
  "entities": {{
    "product_name": "Blue T-Shirt",
    "time_period": "next month"
  }},
  "time_range": "next_30_days",
  "requires_forecast": true
}}

Rules:
- domain: Must be one of the 5 domains listed above
- confidence: Float between 0 and 1
- entities: Key entities mentioned (products, time periods, metrics)
- time_range: One of: last_7_days, last_30_days, last_90_days, next_7_days, next_30_days
- requires_forecast: true if question asks about future predictions

Extract the intent now:"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into intent object"""
        import json
        
        # Clean response
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            intent = json.loads(response_text)
            
            # Validate domain
            if intent.get("domain") not in self.INTENT_DOMAINS:
                logger.warning("invalid_domain",
                             domain=intent.get("domain"),
                             defaulting_to="sales_analysis")
                intent["domain"] = "sales_analysis"
            
            # Ensure confidence is in range
            confidence = intent.get("confidence", 0.5)
            intent["confidence"] = max(0.0, min(1.0, confidence))
            
            # Set defaults
            intent.setdefault("entities", {})
            intent.setdefault("time_range", "last_30_days")
            intent.setdefault("requires_forecast", False)
            
            return intent
            
        except json.JSONDecodeError as e:
            logger.error("intent_parse_error",
                        error=str(e),
                        response=response_text[:200])
            
            # Return safe default
            return {
                "domain": "sales_analysis",
                "confidence": 0.3,
                "entities": {},
                "time_range": "last_30_days",
                "requires_forecast": False
            }