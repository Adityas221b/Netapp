"""
CloudFlux AI - Cloud Storage Routes
API endpoints for listing and managing cloud storage objects
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.auth import get_current_active_user
from app.services.cloud_service import cloud_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/storage", tags=["Cloud Storage"])


@router.get("/objects")
async def get_cloud_objects(
    provider: Optional[str] = None,
    current_user = Depends(get_current_active_user)
):
    """
    Get storage objects from cloud providers
    
    **Requires Authentication**
    
    - **provider**: Filter by provider (AWS, AZURE, GCP). If not provided, returns all.
    
    Returns list of storage objects with metadata
    """
    results = {
        "AWS": [],
        "AZURE": [],
        "GCP": []
    }
    
    try:
        # Fetch from AWS S3
        if not provider or provider.upper() == "AWS":
            try:
                aws_objects = await cloud_service.list_aws_objects()
                results["AWS"] = [
                    {
                        "name": obj["key"],
                        "size": format_size(obj["size"]),
                        "size_bytes": obj["size"],
                        "tier": map_storage_class(obj.get("storage_class", "STANDARD")),
                        "lastAccessed": format_time_ago(obj["last_modified"]),
                        "last_modified": obj["last_modified"],
                        "bucket": f"s3://{obj['bucket']}",
                        "provider": "AWS"
                    }
                    for obj in aws_objects
                ]
                logger.info(f"✅ Retrieved {len(results['AWS'])} objects from AWS")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch AWS objects: {e}")
        
        # Fetch from Azure Blob Storage
        if not provider or provider.upper() == "AZURE":
            try:
                azure_blobs = await cloud_service.list_azure_blobs()
                results["AZURE"] = [
                    {
                        "name": blob["name"],
                        "size": format_size(blob["size"]),
                        "size_bytes": blob["size"],
                        "tier": map_azure_tier(blob.get("access_tier", "Hot")),
                        "lastAccessed": format_time_ago(blob["last_modified"]),
                        "last_modified": blob["last_modified"],
                        "bucket": f"azure-blob://{blob['container']}",
                        "provider": "AZURE"
                    }
                    for blob in azure_blobs
                ]
                logger.info(f"✅ Retrieved {len(results['AZURE'])} objects from Azure")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch Azure objects: {e}")
        
        # Fetch from GCP Cloud Storage
        if not provider or provider.upper() == "GCP":
            try:
                gcp_objects = await cloud_service.list_gcp_objects()
                results["GCP"] = [
                    {
                        "name": obj["name"],
                        "size": format_size(obj["size"]),
                        "size_bytes": obj["size"],
                        "tier": map_gcp_storage_class(obj.get("storage_class", "STANDARD")),
                        "lastAccessed": format_time_ago(obj["last_modified"]),
                        "last_modified": obj["last_modified"],
                        "bucket": f"gs://{obj['bucket']}",
                        "provider": "GCP"
                    }
                    for obj in gcp_objects
                ]
                logger.info(f"✅ Retrieved {len(results['GCP'])} objects from GCP")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch GCP objects: {e}")
        
        # Return filtered or all results
        if provider:
            return {
                "provider": provider.upper(),
                "objects": results.get(provider.upper(), []),
                "count": len(results.get(provider.upper(), []))
            }
        else:
            return {
                "providers": results,
                "total_count": sum(len(objs) for objs in results.values())
            }
    
    except Exception as e:
        logger.error(f"❌ Error fetching cloud objects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_time_ago(iso_time: str) -> str:
    """Format ISO time string to 'X time ago' format"""
    try:
        last_modified = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        now = datetime.now(last_modified.tzinfo)
        diff = now - last_modified
        
        if diff.days > 365:
            return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
        elif diff.days > 30:
            return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hour{'s' if diff.seconds // 3600 > 1 else ''} ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minute{'s' if diff.seconds // 60 > 1 else ''} ago"
        else:
            return "just now"
    except:
        return "unknown"


def map_storage_class(storage_class: str) -> str:
    """Map AWS storage class to HOT/WARM/COLD"""
    mapping = {
        "STANDARD": "HOT",
        "STANDARD_IA": "WARM",
        "ONEZONE_IA": "WARM",
        "INTELLIGENT_TIERING": "WARM",
        "GLACIER": "COLD",
        "GLACIER_IR": "COLD",
        "DEEP_ARCHIVE": "COLD"
    }
    return mapping.get(storage_class, "WARM")


def map_azure_tier(tier: str) -> str:
    """Map Azure access tier to HOT/WARM/COLD"""
    mapping = {
        "Hot": "HOT",
        "Cool": "WARM",
        "Archive": "COLD",
        "Cold": "COLD"
    }
    return mapping.get(tier, "WARM")


def map_gcp_storage_class(storage_class: str) -> str:
    """Map GCP storage class to HOT/WARM/COLD"""
    mapping = {
        "STANDARD": "HOT",
        "NEARLINE": "WARM",
        "COLDLINE": "COLD",
        "ARCHIVE": "COLD"
    }
    return mapping.get(storage_class, "WARM")
