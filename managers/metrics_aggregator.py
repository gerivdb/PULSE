"""MetricsAggregator - Time-series metrics processing

IntentHash¹¹: 0x7E3B9F5A_P3_1_PULSE_COMPLETE_20260303T0313Z

Aggregates and processes time-series metrics.
"""

from typing import Dict, Any, List, Tuple
import time


class MetricsAggregator:
    """Aggregate time-series metrics"""
    
    def __init__(self):
        self.metrics_store = {}
    
    def record_metric(
        self,
        service: str,
        metric_name: str,
        value: float,
        tags: Dict[str, str] = None
    ) -> str:
        """Record metric value
        
        Args:
            service: Service name
            metric_name: Metric name
            value: Metric value
            tags: Optional tags
        
        Returns:
            Status: SUCCESS/FAILED
        """
        try:
            key = f"{service}.{metric_name}"
            
            if key not in self.metrics_store:
                self.metrics_store[key] = []
            
            self.metrics_store[key].append({
                'timestamp': time.time(),
                'value': value,
                'tags': tags or {}
            })
            
            return 'SUCCESS'
        
        except Exception as e:
            return 'FAILED'
    
    def query_metrics(
        self,
        service: str,
        metric_name: str,
        start_time: float = None,
        end_time: float = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Query metrics
        
        Args:
            service: Service name
            metric_name: Metric name
            start_time: Start timestamp
            end_time: End timestamp
        
        Returns:
            Tuple of (status: SUCCESS/FAILED, metrics)
        """
        try:
            key = f"{service}.{metric_name}"
            metrics = self.metrics_store.get(key, [])
            
            # Filter by time range
            if start_time:
                metrics = [m for m in metrics if m['timestamp'] >= start_time]
            if end_time:
                metrics = [m for m in metrics if m['timestamp'] <= end_time]
            
            return 'SUCCESS', metrics
        
        except Exception as e:
            return 'FAILED', []
    
    def aggregate(
        self,
        service: str,
        metric_name: str,
        aggregation: str,
        window: int = 60
    ) -> Tuple[str, float]:
        """Aggregate metrics
        
        Args:
            service: Service name
            metric_name: Metric name
            aggregation: Aggregation function (avg, sum, max, min, count)
            window: Time window in seconds
        
        Returns:
            Tuple of (status: SUCCESS/FAILED, aggregated_value)
        """
        try:
            end_time = time.time()
            start_time = end_time - window
            
            status, metrics = self.query_metrics(service, metric_name, start_time, end_time)
            
            if status != 'SUCCESS' or not metrics:
                return 'FAILED', 0.0
            
            values = [m['value'] for m in metrics]
            
            if aggregation == 'avg':
                result = sum(values) / len(values)
            elif aggregation == 'sum':
                result = sum(values)
            elif aggregation == 'max':
                result = max(values)
            elif aggregation == 'min':
                result = min(values)
            elif aggregation == 'count':
                result = len(values)
            else:
                return 'FAILED', 0.0
            
            return 'SUCCESS', result
        
        except Exception as e:
            return 'FAILED', 0.0
    
    def detect_anomaly(
        self,
        service: str,
        metric_name: str,
        threshold: float
    ) -> Tuple[str, bool]:
        """Detect metric anomalies
        
        Args:
            service: Service name
            metric_name: Metric name
            threshold: Anomaly threshold
        
        Returns:
            Tuple of (status: SUCCESS/FAILED, is_anomaly)
        """
        try:
            # Compute recent average
            status, avg_value = self.aggregate(service, metric_name, 'avg', window=300)
            
            if status != 'SUCCESS':
                return 'FAILED', False
            
            # Check if exceeds threshold
            is_anomaly = avg_value > threshold
            
            return 'SUCCESS', is_anomaly
        
        except Exception as e:
            return 'FAILED', False
