"""
Query Executor
Stage 4: Executes queries and applies forecasting
"""

import structlog
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np

from config import settings

logger = structlog.get_logger()


class QueryExecutor:
    """
    Executes ShopifyQL queries and applies forecasting
    
    In production, this would call the Shopify Analytics API.
    In demo mode, it generates synthetic data.
    """
    
    def __init__(self):
        """Initialize the query executor"""
        self.demo_mode = settings.DEMO_MODE
        logger.info("query_executor_initialized", demo_mode=self.demo_mode)
    
    async def execute(
        self,
        query: str,
        shop_domain: str,
        access_token: str,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a ShopifyQL query
        
        Args:
            query: ShopifyQL query string
            shop_domain: Shopify shop domain
            access_token: Shopify access token
            plan: Query execution plan
            
        Returns:
            Execution result with data and metadata
        """
        logger.info("executing_query",
                   query=query[:100],
                   shop_domain=shop_domain,
                   demo_mode=self.demo_mode)
        
        try:
            # In demo mode, generate synthetic data
            if self.demo_mode:
                data = self._generate_synthetic_data(query, plan)
            else:
                # In production, call Shopify Analytics API
                data = await self._execute_shopify_query(query, shop_domain, access_token)
            
            # Apply forecasting if needed
            if plan.get("requires_forecast"):
                forecast = self._apply_forecasting(data, plan.get("forecast_config", {}))
                data = self._merge_forecast_with_data(data, forecast)
                forecast_applied = True
            else:
                forecast_applied = False
            
            result = {
                "data": data,
                "forecast_applied": forecast_applied,
                "row_count": len(data),
                "query_executed": query
            }
            
            logger.info("query_executed",
                       row_count=len(data),
                       forecast_applied=forecast_applied)
            
            return result
            
        except Exception as e:
            logger.error("query_execution_failed",
                        error=str(e),
                        exc_info=True)
            
            return {
                "data": [],
                "forecast_applied": False,
                "row_count": 0,
                "error": str(e)
            }
    
    def _generate_synthetic_data(self, query: str, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate synthetic data for demo mode"""
        query_upper = query.upper()
        
        # Determine what kind of data to generate based on query
        if "INVENTORY" in query_upper or "STOCK" in query_upper:
            return self._generate_inventory_data(plan)
        elif "CUSTOMER" in query_upper:
            return self._generate_customer_data(plan)
        elif "TOP" in query_upper or "LIMIT 5" in query_upper:
            return self._generate_ranking_data(plan, limit=5)
        else:
            return self._generate_sales_data(plan)
    
    def _generate_sales_data(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate synthetic sales data"""
        products = [
            "Blue T-Shirt", "Red Hoodie", "Black Jeans", 
            "White Sneakers", "Green Cap"
        ]
        
        # Generate 90 days of historical data
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        for product in products[:3]:  # Use top 3 products
            current_date = start_date
            base_quantity = np.random.randint(5, 15)
            
            while current_date <= end_date:
                # Add some randomness and trend
                trend = (current_date - start_date).days * 0.01
                noise = np.random.normal(0, 2)
                quantity = max(0, int(base_quantity + trend + noise))
                
                data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "product_name": product,
                    "quantity": quantity,
                    "total_sales": quantity * np.random.uniform(20, 50)
                })
                
                current_date += timedelta(days=1)
        
        return data
    
    def _generate_inventory_data(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate synthetic inventory data"""
        products = [
            {"name": "Blue T-Shirt", "current_stock": 45, "daily_velocity": 8},
            {"name": "Red Hoodie", "current_stock": 120, "daily_velocity": 5},
            {"name": "Black Jeans", "current_stock": 15, "daily_velocity": 12},
            {"name": "White Sneakers", "current_stock": 8, "daily_velocity": 10},
            {"name": "Green Cap", "current_stock": 200, "daily_velocity": 3},
        ]
        
        data = []
        for product in products:
            days_until_stockout = product["current_stock"] / product["daily_velocity"] if product["daily_velocity"] > 0 else 999
            
            data.append({
                "product_name": product["name"],
                "inventory_quantity": product["current_stock"],
                "daily_velocity": product["daily_velocity"],
                "days_until_stockout": round(days_until_stockout, 1)
            })
        
        return data
    
    def _generate_customer_data(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate synthetic customer data"""
        customers = [
            {"email": "john.smith@example.com", "orders": 5, "total_spent": 450.00},
            {"email": "sarah.jones@example.com", "orders": 3, "total_spent": 280.00},
            {"email": "mike.brown@example.com", "orders": 7, "total_spent": 620.00},
            {"email": "emma.davis@example.com", "orders": 4, "total_spent": 380.00},
            {"email": "alex.wilson@example.com", "orders": 2, "total_spent": 190.00},
        ]
        
        # Filter to customers with repeat orders
        return [c for c in customers if c["orders"] > 1]
    
    def _generate_ranking_data(self, plan: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Generate synthetic ranking data"""
        products = [
            {"name": "Blue T-Shirt", "quantity": 680, "revenue": 13600},
            {"name": "Red Hoodie", "quantity": 420, "revenue": 16800},
            {"name": "Black Jeans", "quantity": 350, "revenue": 21000},
            {"name": "White Sneakers", "quantity": 290, "revenue": 23200},
            {"name": "Green Cap", "quantity": 180, "revenue": 3600},
        ]
        
        return products[:limit]
    
    async def _execute_shopify_query(
        self,
        query: str,
        shop_domain: str,
        access_token: str
    ) -> List[Dict[str, Any]]:
        """Execute actual Shopify Analytics query (production mode)"""
        # This would call the Shopify Analytics API
        # For now, return empty list as placeholder
        logger.warning("shopify_api_not_implemented",
                      message="Real Shopify API calls not implemented yet")
        return []
    
    def _apply_forecasting(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply linear regression forecasting to historical data
        
        Args:
            data: Historical data points
            config: Forecast configuration
            
        Returns:
            Forecast results with predictions
        """
        logger.info("applying_forecast",
                   data_points=len(data),
                   method=config.get("method"))
        
        if not data:
            return {"forecast": [], "method": "none"}
        
        # Group data by product
        products = {}
        for row in data:
            product = row.get("product_name", "unknown")
            if product not in products:
                products[product] = []
            products[product].append(row)
        
        forecasts = {}
        
        for product_name, product_data in products.items():
            # Extract quantities and create time series
            quantities = [row.get("quantity", 0) for row in product_data]
            
            if len(quantities) < 7:  # Need at least a week of data
                continue
            
            # Linear regression using numpy
            X = np.arange(len(quantities)).reshape(-1, 1)
            y = np.array(quantities)
            
            # Calculate slope and intercept
            slope, intercept = self._calculate_linear_regression(X.flatten(), y)
            
            # Forecast future values
            forecast_days = config.get("forecast_days", 30)
            future_X = np.arange(len(quantities), len(quantities) + forecast_days)
            predictions = slope * future_X + intercept
            predictions = np.maximum(predictions, 0)  # No negative predictions
            
            # Calculate daily velocity
            daily_velocity = np.mean(quantities[-30:]) if len(quantities) >= 30 else np.mean(quantities)
            
            # Total forecast with safety stock
            total_forecast = np.sum(predictions)
            safety_stock = total_forecast * (settings.SAFETY_STOCK_MULTIPLIER - 1)
            total_with_safety = total_forecast + safety_stock
            
            forecasts[product_name] = {
                "daily_velocity": round(daily_velocity, 1),
                "forecast_quantity": round(total_forecast, 0),
                "safety_stock": round(safety_stock, 0),
                "total_needed": round(total_with_safety, 0),
                "forecast_days": forecast_days,
                "confidence": self._calculate_forecast_confidence(quantities, predictions[:len(quantities)])
            }
        
        return {
            "forecasts": forecasts,
            "method": "linear_regression",
            "config": config
        }
    
    def _calculate_linear_regression(self, X: np.ndarray, y: np.ndarray) -> tuple:
        """Calculate linear regression slope and intercept"""
        n = len(X)
        X_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X - X_mean) * (y - y_mean))
        denominator = np.sum((X - X_mean) ** 2)
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * X_mean
        
        return slope, intercept
    
    def _calculate_forecast_confidence(
        self,
        actual: List[float],
        predicted: np.ndarray
    ) -> float:
        """Calculate forecast confidence based on R-squared"""
        if len(actual) != len(predicted):
            predicted = predicted[:len(actual)]
        
        actual_array = np.array(actual)
        ss_res = np.sum((actual_array - predicted) ** 2)
        ss_tot = np.sum((actual_array - np.mean(actual_array)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Convert R-squared to confidence (0.0 to 1.0)
        return max(0.0, min(1.0, r_squared))
    
    def _merge_forecast_with_data(
        self,
        data: List[Dict[str, Any]],
        forecast: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Merge forecast results into data"""
        forecasts = forecast.get("forecasts", {})
        
        # Add forecast info to each product's data
        for row in data:
            product_name = row.get("product_name")
            if product_name in forecasts:
                row["forecast"] = forecasts[product_name]
        
        return data