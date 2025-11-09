"""Analytics API endpoints."""
from fastapi import APIRouter
from datetime import datetime, timedelta
import random

from app.models.data_models import StorageTier
from app.api.data import data_objects_store
from app.api.migration import migration_jobs_store
from app.services.classifier import classifier

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview():
    """Get overall analytics dashboard data."""
    total_objects = len(data_objects_store)
    total_size = sum(obj.size_gb for obj in data_objects_store.values())
    total_cost = sum(obj.monthly_cost for obj in data_objects_store.values())
    
    # Tier distribution
    tier_counts = {tier.value: 0 for tier in StorageTier}
    tier_sizes = {tier.value: 0.0 for tier in StorageTier}
    tier_costs = {tier.value: 0.0 for tier in StorageTier}
    
    for obj in data_objects_store.values():
        tier_counts[obj.current_tier.value] += 1
        tier_sizes[obj.current_tier.value] += obj.size_gb
        tier_costs[obj.current_tier.value] += obj.monthly_cost
    
    # Migration stats
    migrations_total = len(migration_jobs_store)
    migrations_completed = sum(1 for job in migration_jobs_store.values() if job.status == "completed")
    migrations_in_progress = sum(1 for job in migration_jobs_store.values() if job.status == "in_progress")
    
    return {
        "summary": {
            "total_objects": total_objects,
            "total_size_gb": round(total_size, 2),
            "total_monthly_cost": round(total_cost, 2),
            "average_cost_per_gb": round(total_cost / total_size, 4) if total_size > 0 else 0
        },
        "tier_distribution": {
            "counts": tier_counts,
            "sizes_gb": {k: round(v, 2) for k, v in tier_sizes.items()},
            "costs": {k: round(v, 2) for k, v in tier_costs.items()}
        },
        "migration_stats": {
            "total_jobs": migrations_total,
            "completed": migrations_completed,
            "in_progress": migrations_in_progress,
            "pending": migrations_total - migrations_completed - migrations_in_progress
        }
    }


@router.get("/costs")
async def get_cost_breakdown():
    """Get detailed cost breakdown."""
    # Current costs
    current_cost = sum(obj.monthly_cost for obj in data_objects_store.values())
    
    # Potential savings if all objects optimally placed
    potential_savings = 0.0
    optimized_cost = 0.0
    
    for obj in data_objects_store.values():
        # Classify to get optimal tier
        classification = classifier.classify(
            file_id=obj.file_id,
            access_frequency=obj.access_count_30d,
            last_accessed=obj.last_accessed,
            size_gb=obj.size_gb
        )
        
        optimal_cost = classification.estimated_cost_per_month
        optimized_cost += optimal_cost
        
        if classification.tier != obj.current_tier:
            potential_savings += (obj.monthly_cost - optimal_cost)
    
    savings_percentage = (potential_savings / current_cost * 100) if current_cost > 0 else 0
    
    return {
        "current_monthly_cost": round(current_cost, 2),
        "optimized_monthly_cost": round(optimized_cost, 2),
        "potential_monthly_savings": round(potential_savings, 2),
        "potential_annual_savings": round(potential_savings * 12, 2),
        "savings_percentage": round(savings_percentage, 2),
        "cost_by_tier": {
            tier.value: round(
                sum(obj.monthly_cost for obj in data_objects_store.values() 
                    if obj.current_tier == tier), 
                2
            )
            for tier in StorageTier
        }
    }


@router.get("/performance")
async def get_performance_metrics():
    """Get performance metrics."""
    if not data_objects_store:
        return {
            "avg_latency_ms": 0,
            "classification_time_ms": 0,
            "objects_classified_per_second": 0
        }
    
    # Calculate average latency based on tier distribution
    total_latency = 0
    for obj in data_objects_store.values():
        total_latency += classifier.latency[obj.current_tier]
    
    avg_latency = total_latency / len(data_objects_store)
    
    # Simulated metrics
    classification_time = random.uniform(50, 100)  # 50-100ms per object
    objects_per_second = 1000 / classification_time
    
    return {
        "avg_latency_ms": round(avg_latency, 2),
        "classification_time_ms": round(classification_time, 2),
        "objects_classified_per_second": round(objects_per_second, 2),
        "total_objects_classified": len(data_objects_store),
        "latency_by_tier": {
            tier.value: classifier.latency[tier] 
            for tier in StorageTier
        }
    }


@router.get("/trends")
async def get_trends():
    """Get historical trends (simulated)."""
    # Simulate 7 days of data
    days = 7
    trends = []
    
    base_objects = len(data_objects_store) or 100
    base_cost = sum(obj.monthly_cost for obj in data_objects_store.values()) or 1000
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        
        # Add some variation
        objects = int(base_objects * (0.8 + random.random() * 0.4))
        cost = base_cost * (0.8 + random.random() * 0.4)
        
        trends.append({
            "date": date,
            "total_objects": objects,
            "total_cost": round(cost, 2),
            "hot_objects": int(objects * 0.3),
            "warm_objects": int(objects * 0.5),
            "cold_objects": int(objects * 0.2)
        })
    
    return {
        "trends": trends,
        "period_days": days
    }


@router.get("/savings")
async def get_potential_savings():
    """Get list of objects with potential savings."""
    savings_opportunities = []
    
    for obj in data_objects_store.values():
        # Classify to get optimal tier
        classification = classifier.classify(
            file_id=obj.file_id,
            access_frequency=obj.access_count_30d,
            last_accessed=obj.last_accessed,
            size_gb=obj.size_gb
        )
        
        if classification.tier != obj.current_tier:
            savings = classifier.calculate_savings(
                obj.current_tier,
                classification.tier,
                obj.size_gb
            )
            
            if savings.monthly_savings > 0:
                savings_opportunities.append({
                    "file_id": obj.file_id,
                    "file_name": obj.file_name,
                    "size_gb": obj.size_gb,
                    "current_tier": obj.current_tier.value,
                    "recommended_tier": classification.tier.value,
                    "monthly_savings": savings.monthly_savings,
                    "annual_savings": savings.annual_savings,
                    "savings_percentage": savings.savings_percentage,
                    "reason": classification.reason
                })
    
    # Sort by savings amount
    savings_opportunities.sort(key=lambda x: x["monthly_savings"], reverse=True)
    
    total_monthly_savings = sum(opp["monthly_savings"] for opp in savings_opportunities)
    
    return {
        "total_opportunities": len(savings_opportunities),
        "total_monthly_savings": round(total_monthly_savings, 2),
        "total_annual_savings": round(total_monthly_savings * 12, 2),
        "opportunities": savings_opportunities[:50]  # Top 50
    }
