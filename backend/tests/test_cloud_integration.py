"""Integration tests for real cloud provider connections"""
import pytest
import os
from app.services.cloud_service import CloudService


@pytest.mark.integration
class TestCloudIntegration:
    """Test suite for real cloud provider integration"""
    
    def setup_method(self):
        """Setup cloud service"""
        self.cloud_service = CloudService()
    
    def test_aws_connection(self):
        """Test AWS S3 connection with real credentials"""
        status = self.cloud_service.get_status()
        assert status['aws_connected'] is True, "AWS S3 should be connected"
    
    def test_azure_connection(self):
        """Test Azure Blob Storage connection"""
        status = self.cloud_service.get_status()
        assert status['azure_connected'] is True, "Azure should be connected"
    
    def test_gcp_connection(self):
        """Test GCP Cloud Storage connection"""
        status = self.cloud_service.get_status()
        assert status['gcp_connected'] is True, "GCP should be connected"
    
    @pytest.mark.asyncio
    async def test_aws_list_objects(self):
        """Test listing objects from AWS S3"""
        objects = await self.cloud_service.list_aws_objects()
        assert isinstance(objects, list)
        # Objects should have required fields
        if len(objects) > 0:
            assert 'key' in objects[0]
            assert 'size' in objects[0]
    
    @pytest.mark.asyncio
    async def test_multi_cloud_aggregation(self):
        """Test aggregating objects from all cloud providers"""
        all_objects = await self.cloud_service.list_all_objects()
        assert isinstance(all_objects, list)
        
        # Verify objects have provider tags
        if len(all_objects) > 0:
            providers = set(obj.get('provider') for obj in all_objects)
            assert len(providers) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
