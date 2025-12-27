"""
Agent Orchestrator
Coordinates the 5-stage AI agent pipeline
"""

import structlog
from typing import Dict, Any, Optional

from .intent_classifier import IntentClassifier
from .query_planner import QueryPlanner
from .shopifyql_generator import ShopifyQLGenerator
from .query_executor import QueryExecutor
from .insight_synthesizer import InsightSynthesizer

logger = structlog.get_logger()


class AgentOrchestrator:
    """
    Orchestrates the 5-stage agent pipeline for query processing
    
    Pipeline stages:
    1. Intent Classification - Understand what the user is asking
    2. Query Planning - Determine data sources and aggregations needed
    3. ShopifyQL Generation - Create the analytics query
    4. Query Execution - Execute query and apply forecasting
    5. Insight Synthesis - Transform data into business-friendly insights
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the orchestrator with all agent components
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        
        # Initialize all agent components
        self.intent_classifier = IntentClassifier(api_key, model)
        self.query_planner = QueryPlanner(api_key, model)
        self.shopifyql_generator = ShopifyQLGenerator(api_key, model)
        self.query_executor = QueryExecutor()
        self.insight_synthesizer = InsightSynthesizer(api_key, model)
        
        logger.info("orchestrator_initialized", model=model)
    
    async def process_query(
        self,
        question: str,
        shop_domain: str,
        access_token: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the complete 5-stage pipeline
        
        Args:
            question: Natural language question
            shop_domain: Shopify shop domain
            access_token: Shopify access token
            context: Additional context information
            
        Returns:
            Complete query response with insights
        """
        logger.info("pipeline_started", question=question[:100], shop_domain=shop_domain)
        
        try:
            # Stage 1: Intent Classification
            logger.info("stage_1_intent_classification")
            intent = await self.intent_classifier.classify(question)
            logger.info("stage_1_completed", 
                       domain=intent.get("domain"),
                       confidence=intent.get("confidence"))
            
            # Stage 2: Query Planning
            logger.info("stage_2_query_planning")
            plan = await self.query_planner.plan(question, intent)
            logger.info("stage_2_completed",
                       data_sources=plan.get("data_sources"),
                       requires_forecast=plan.get("requires_forecast"))
            
            # Stage 3: ShopifyQL Generation
            logger.info("stage_3_shopifyql_generation")
            query = await self.shopifyql_generator.generate(question, intent, plan)
            logger.info("stage_3_completed", query=query[:100] if query else None)
            
            # Stage 4: Query Execution
            logger.info("stage_4_query_execution")
            execution_result = await self.query_executor.execute(
                query=query,
                shop_domain=shop_domain,
                access_token=access_token,
                plan=plan
            )
            logger.info("stage_4_completed",
                       data_points=len(execution_result.get("data", [])))
            
            # Stage 5: Insight Synthesis
            logger.info("stage_5_insight_synthesis")
            insights = await self.insight_synthesizer.synthesize(
                question=question,
                intent=intent,
                plan=plan,
                query=query,
                execution_result=execution_result
            )
            logger.info("stage_5_completed")
            
            # Calculate overall confidence
            overall_confidence = self._calculate_confidence(intent, execution_result)
            
            # Build final response
            response = {
                "status": "completed",
                "intent": intent,
                "query": query,
                "insights": insights,
                "confidence": overall_confidence,
                "metadata": {
                    "shop_domain": shop_domain,
                    "data_points": len(execution_result.get("data", [])),
                    "forecast_applied": execution_result.get("forecast_applied", False)
                }
            }
            
            logger.info("pipeline_completed", 
                       status="success",
                       confidence=overall_confidence)
            
            return response
            
        except Exception as e:
            logger.error("pipeline_failed",
                        question=question[:100],
                        error_type=type(e).__name__,
                        error_message=str(e),
                        exc_info=True)
            
            return {
                "status": "failed",
                "intent": {},
                "query": "",
                "insights": {
                    "summary": "Failed to process query",
                    "key_findings": [],
                    "recommendations": [],
                    "data_summary": {}
                },
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _calculate_confidence(
        self,
        intent: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence score based on intent and execution
        
        Args:
            intent: Intent classification result
            execution_result: Query execution result
            
        Returns:
            Confidence score between 0 and 1
        """
        # Start with intent confidence
        intent_confidence = intent.get("confidence", 0.5)
        
        # Adjust based on data availability
        data_available = len(execution_result.get("data", [])) > 0
        data_confidence = 1.0 if data_available else 0.5
        
        # Weight: 60% intent, 40% data
        overall = (intent_confidence * 0.6) + (data_confidence * 0.4)
        
        # Ensure bounds
        return max(0.0, min(1.0, overall))