"""Unit tests for data classification engine"""
import pytest
from datetime import datetime, timedelta
from app.services.placement_optimizer import (
    PlacementOptimizer,
    DataProfile,
    StorageOption
)


class TestDataClassification:
    """Test suite for data temperature classification"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.optimizer = PlacementOptimizer()
    
    def test_hot_data_classification(self):
        """Test HOT tier classification for frequently accessed data"""
        profile = DataProfile(
            file_name="hot_file.csv",
            size_gb=0.5,
            access_count_7d=15,
            access_count_30d=50,
            last_accessed=datetime.now() - timedelta(hours=12),
            current_provider="AWS",
            current_tier="HOT"
        )
        
        temperature = self.optimizer.classify_data_temperature(profile)
        assert temperature == "HOT"
    
    def test_warm_data_classification(self):
        """Test WARM tier classification for moderately accessed data"""
        profile = DataProfile(
            file_name="warm_file.csv",
            size_gb=5.0,
            access_count_7d=3,
            access_count_30d=8,
            last_accessed=datetime.now() - timedelta(days=10),
            current_provider="AWS",
            current_tier="WARM"
        )
        
        temperature = self.optimizer.classify_data_temperature(profile)
        assert temperature == "WARM"
    
    def test_cold_data_classification(self):
        """Test COLD tier classification for rarely accessed data"""
        profile = DataProfile(
            file_name="cold_file.csv",
            size_gb=20.0,
            access_count_7d=0,
            access_count_30d=2,
            last_accessed=datetime.now() - timedelta(days=45),
            current_provider="AWS",
            current_tier="COLD"
        )
        
        temperature = self.optimizer.classify_data_temperature(profile)
        assert temperature == "COLD"
    
    def test_archive_data_classification(self):
        """Test ARCHIVE tier classification for old data"""
        profile = DataProfile(
            file_name="archive_file.csv",
            size_gb=100.0,
            access_count_7d=0,
            access_count_30d=0,
            last_accessed=datetime.now() - timedelta(days=120),
            current_provider="AWS",
            current_tier="ARCHIVE"
        )
        
        temperature = self.optimizer.classify_data_temperature(profile)
        assert temperature == "ARCHIVE"
    
    def test_cost_calculation(self):
        """Test monthly cost calculation"""
        size_gb = 10.0
        storage_cost = 0.023  # AWS HOT
        retrieval_cost = 0.0
        access_frequency = 10
        
        total_cost = self.optimizer.calculate_monthly_cost(
            size_gb, storage_cost, retrieval_cost, access_frequency
        )
        
        expected_cost = 10.0 * 0.023  # Only storage cost
        assert abs(total_cost - expected_cost) < 0.001
    
    def test_placement_optimization(self):
        """Test optimal placement recommendation"""
        profile = DataProfile(
            file_name="test_file.csv",
            size_gb=5.0,
            access_count_7d=2,
            access_count_30d=5,
            last_accessed=datetime.now() - timedelta(days=8),
            current_provider="AWS",
            current_tier="HOT"  # Currently in expensive tier
        )
        
        recommendations = self.optimizer.recommend_optimal_placement(profile, top_n=3)
        
        assert len(recommendations) == 3
        best_option, best_score, temperature = recommendations[0]
        
        # Should recommend WARM tier for this access pattern
        assert temperature in ["WARM", "COLD"]
        assert best_score > 0
    
    def test_savings_calculation(self):
        """Test potential savings calculation"""
        profile = DataProfile(
            file_name="misplaced_file.csv",
            size_gb=50.0,
            access_count_7d=0,
            access_count_30d=1,
            last_accessed=datetime.now() - timedelta(days=60),
            current_provider="AWS",
            current_tier="HOT"  # Expensive tier for cold data
        )
        
        analysis = self.optimizer.analyze_current_placement(profile)
        
        assert not analysis["is_optimal"]
        assert analysis["potential_savings"]["monthly_usd"] > 0
        assert analysis["data_temperature"] == "COLD"


class TestStorageCosts:
    """Test suite for storage cost calculations"""
    
    def setup_method(self):
        self.optimizer = PlacementOptimizer()
    
    def test_aws_pricing(self):
        """Verify AWS pricing structure"""
        assert self.optimizer.STORAGE_COSTS["AWS"]["HOT"] == 0.023
        assert self.optimizer.STORAGE_COSTS["AWS"]["WARM"] == 0.0125
        assert self.optimizer.STORAGE_COSTS["AWS"]["COLD"] == 0.004
    
    def test_azure_pricing(self):
        """Verify Azure pricing structure"""
        assert self.optimizer.STORAGE_COSTS["AZURE"]["HOT"] == 0.0208
        assert self.optimizer.STORAGE_COSTS["AZURE"]["COOL"] == 0.0152
    
    def test_gcp_pricing(self):
        """Verify GCP pricing structure"""
        assert self.optimizer.STORAGE_COSTS["GCP"]["HOT"] == 0.020
        assert self.optimizer.STORAGE_COSTS["GCP"]["WARM"] == 0.010


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
