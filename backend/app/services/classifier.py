"""Data Classification Engine - Core component of CloudFlux AI."""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from app.models.data_models import StorageTier, ClassificationResult, CostSavings
from app.config import settings

logger = logging.getLogger(__name__)


class DataClassifier:
    """Intelligent data classification engine."""
    
    def __init__(self):
        """Initialize the classifier with cost and latency configurations."""
        # Cost per GB per month (USD)
        self.costs = {
            StorageTier.HOT: settings.cost_hot_storage,
            StorageTier.WARM: settings.cost_warm_storage,
            StorageTier.COLD: settings.cost_cold_storage
        }
        
        # Latency in milliseconds
        self.latency = {
            StorageTier.HOT: settings.latency_hot,
            StorageTier.WARM: settings.latency_warm,
            StorageTier.COLD: settings.latency_cold
        }
        
        logger.info(f"DataClassifier initialized with costs: {self.costs}")
    
    def classify(
        self,
        file_id: str,
        access_frequency: int,
        last_accessed: datetime,
        size_gb: float,
        latency_requirement_ms: int = None
    ) -> ClassificationResult:
        """
        Classify data into storage tiers based on access patterns.
        
        Args:
            file_id: Unique identifier for the file
            access_frequency: Number of accesses in last 30 days
            last_accessed: Last access timestamp
            size_gb: Data size in GB
            latency_requirement_ms: Required latency (optional)
        
        Returns:
            Classification result with tier, cost, and reasoning
        """
        days_since_access = (datetime.now() - last_accessed).days if last_accessed else 999
        
        # Rule-based classification with priority
        tier, reason, confidence = self._determine_tier(
            access_frequency,
            days_since_access,
            latency_requirement_ms
        )
        
        monthly_cost = self.costs[tier] * size_gb
        
        result = ClassificationResult(
            file_id=file_id,
            tier=tier,
            reason=reason,
            estimated_cost_per_month=round(monthly_cost, 4),
            latency_ms=self.latency[tier],
            access_frequency=access_frequency,
            days_since_access=days_since_access,
            confidence=confidence
        )
        
        logger.info(f"Classified {file_id}: {tier} (confidence: {confidence})")
        return result
    
    def _determine_tier(
        self,
        access_frequency: int,
        days_since_access: int,
        latency_requirement_ms: int = None
    ) -> Tuple[StorageTier, str, float]:
        """
        Determine the appropriate storage tier.
        
        Returns:
            Tuple of (tier, reason, confidence)
        """
        # Priority 1: Latency requirements (if specified)
        if latency_requirement_ms is not None:
            if latency_requirement_ms < 100:
                return (
                    StorageTier.HOT,
                    f"Low latency requirement ({latency_requirement_ms}ms < 100ms)",
                    0.95
                )
            elif latency_requirement_ms < 1000:
                return (
                    StorageTier.WARM,
                    f"Moderate latency requirement ({latency_requirement_ms}ms)",
                    0.90
                )
        
        # Priority 2: High access frequency
        if access_frequency > 100:
            return (
                StorageTier.HOT,
                f"High access frequency ({access_frequency} > 100 accesses/month)",
                0.92
            )
        
        # Priority 3: Recent access with moderate frequency
        if access_frequency > 10 and days_since_access < 30:
            return (
                StorageTier.WARM,
                f"Moderate access ({access_frequency} accesses) and recently used ({days_since_access} days ago)",
                0.85
            )
        
        # Priority 4: Old data
        if days_since_access > 90:
            return (
                StorageTier.COLD,
                f"Not accessed in {days_since_access} days (> 90 days)",
                0.90
            )
        
        # Priority 5: Low access frequency
        if access_frequency < 5:
            return (
                StorageTier.COLD,
                f"Low access frequency ({access_frequency} < 5 accesses/month)",
                0.88
            )
        
        # Default: Balanced tier
        return (
            StorageTier.WARM,
            f"Balanced access pattern ({access_frequency} accesses, {days_since_access} days since last access)",
            0.75
        )
    
    def calculate_savings(
        self,
        current_tier: StorageTier,
        recommended_tier: StorageTier,
        size_gb: float
    ) -> CostSavings:
        """
        Calculate potential cost savings from tier optimization.
        
        Args:
            current_tier: Current storage tier
            recommended_tier: Recommended storage tier
            size_gb: Data size in GB
        
        Returns:
            Cost savings breakdown
        """
        current_cost = self.costs[current_tier] * size_gb
        recommended_cost = self.costs[recommended_tier] * size_gb
        savings = current_cost - recommended_cost
        savings_pct = (savings / current_cost * 100) if current_cost > 0 else 0
        
        return CostSavings(
            current_monthly_cost=round(current_cost, 4),
            recommended_monthly_cost=round(recommended_cost, 4),
            monthly_savings=round(savings, 4),
            savings_percentage=round(savings_pct, 2),
            annual_savings=round(savings * 12, 2)
        )
    
    def batch_classify(
        self,
        data_objects: List[Dict]
    ) -> Dict[str, ClassificationResult]:
        """
        Classify multiple data objects at once.
        
        Args:
            data_objects: List of data object dictionaries
        
        Returns:
            Dictionary mapping file_id to classification result
        """
        results = {}
        
        for obj in data_objects:
            try:
                result = self.classify(
                    file_id=obj['file_id'],
                    access_frequency=obj.get('access_count_30d', 0),
                    last_accessed=obj.get('last_accessed'),
                    size_gb=obj.get('size_gb', 0.0),
                    latency_requirement_ms=obj.get('latency_requirement_ms')
                )
                results[obj['file_id']] = result
            except Exception as e:
                logger.error(f"Error classifying {obj.get('file_id')}: {e}")
        
        logger.info(f"Batch classified {len(results)} objects")
        return results
    
    def get_tier_distribution(
        self,
        classifications: Dict[str, ClassificationResult]
    ) -> Dict[str, int]:
        """
        Get distribution of files across tiers.
        
        Args:
            classifications: Dictionary of classification results
        
        Returns:
            Dictionary with count per tier
        """
        distribution = {
            StorageTier.HOT: 0,
            StorageTier.WARM: 0,
            StorageTier.COLD: 0
        }
        
        for result in classifications.values():
            distribution[result.tier] += 1
        
        return {tier.value: count for tier, count in distribution.items()}
    
    def calculate_total_savings(
        self,
        current_tiers: Dict[str, Tuple[StorageTier, float]],
        recommended_tiers: Dict[str, Tuple[StorageTier, float]]
    ) -> float:
        """
        Calculate total savings from tier optimizations.
        
        Args:
            current_tiers: Dict of file_id -> (current_tier, size_gb)
            recommended_tiers: Dict of file_id -> (recommended_tier, size_gb)
        
        Returns:
            Total monthly savings in USD
        """
        total_savings = 0.0
        
        for file_id, (rec_tier, size_gb) in recommended_tiers.items():
            if file_id in current_tiers:
                curr_tier, _ = current_tiers[file_id]
                savings = self.calculate_savings(curr_tier, rec_tier, size_gb)
                total_savings += savings.monthly_savings
        
        return round(total_savings, 2)


# Global classifier instance
classifier = DataClassifier()
