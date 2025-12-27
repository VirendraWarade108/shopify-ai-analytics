"""
AI Agent Package

This package contains the 5-stage agent pipeline for processing analytics queries:
1. Intent Classification
2. Query Planning
3. ShopifyQL Generation
4. Query Execution
5. Insight Synthesis
"""

from .orchestrator import AgentOrchestrator
from .intent_classifier import IntentClassifier
from .query_planner import QueryPlanner
from .shopifyql_generator import ShopifyQLGenerator
from .query_executor import QueryExecutor
from .insight_synthesizer import InsightSynthesizer

__all__ = [
    "AgentOrchestrator",
    "IntentClassifier",
    "QueryPlanner",
    "ShopifyQLGenerator",
    "QueryExecutor",
    "InsightSynthesizer",
]