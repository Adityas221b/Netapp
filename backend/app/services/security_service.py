"""
Security and Encryption Service
Implements encryption at rest, in transit, and location-based access control
"""
import logging
import base64
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataClassification(Enum):
    """Data sensitivity classification"""
    GENERAL = "general"
    PII = "pii"  # Personally Identifiable Information
    PHI = "phi"  # Protected Health Information
    FINANCIAL = "financial"
    INTELLECTUAL_PROPERTY = "ip"


class AccessControlService:
    """
    Role-Based Access Control (RBAC) service
    """
    
    # Define role permissions
    ROLE_PERMISSIONS = {
        "admin": {
            "read": ["*"],
            "write": ["*"],
            "delete": ["*"],
            "manage_users": True,
            "manage_policies": True,
        },
        "data_engineer": {
            "read": ["*"],
            "write": ["general", "internal"],
            "delete": ["general"],
            "manage_users": False,
            "manage_policies": False,
        },
        "analyst": {
            "read": ["general", "internal"],
            "write": [],
            "delete": [],
            "manage_users": False,
            "manage_policies": False,
        },
        "viewer": {
            "read": ["general"],
            "write": [],
            "delete": [],
            "manage_users": False,
            "manage_policies": False,
        }
    }
    
    # Location-based restrictions
    LOCATION_POLICIES = {
        "eu": {
            "allowed_providers": ["AWS", "AZURE", "GCP"],
            "allowed_regions": ["eu-west-1", "eu-central-1", "westeurope", "europe-west1"],
            "data_residency": True,
            "requires_encryption": True,
        },
        "us": {
            "allowed_providers": ["AWS", "AZURE", "GCP"],
            "allowed_regions": ["us-east-1", "us-west-2", "eastus", "us-central1"],
            "data_residency": False,
            "requires_encryption": True,
        },
        "apac": {
            "allowed_providers": ["AWS", "AZURE", "GCP"],
            "allowed_regions": ["ap-southeast-1", "southeastasia", "asia-southeast1"],
            "data_residency": True,
            "requires_encryption": True,
        }
    }
    
    def __init__(self):
        """Initialize access control service"""
        self.audit_log: List[Dict] = []
    
    def check_permission(
        self,
        user_role: str,
        action: str,
        data_classification: str
    ) -> bool:
        """
        Check if user role has permission for action on data
        
        Args:
            user_role: User's role
            action: Action to perform (read, write, delete)
            data_classification: Data sensitivity level
            
        Returns:
            True if permitted, False otherwise
        """
        if user_role not in self.ROLE_PERMISSIONS:
            logger.warning(f"❌ Unknown role: {user_role}")
            return False
        
        permissions = self.ROLE_PERMISSIONS[user_role]
        
        if action not in permissions:
            return False
        
        allowed_classifications = permissions[action]
        
        # Wildcard permission
        if "*" in allowed_classifications:
            logger.debug(f"✅ Permission granted: {user_role} can {action} {data_classification}")
            return True
        
        # Check specific classification
        if data_classification in allowed_classifications:
            logger.debug(f"✅ Permission granted: {user_role} can {action} {data_classification}")
            return True
        
        logger.warning(f"❌ Permission denied: {user_role} cannot {action} {data_classification}")
        return False
    
    def validate_location_policy(
        self,
        location: str,
        provider: str,
        region: str,
        data_classification: DataClassification
    ) -> Tuple[bool, str]:
        """
        Validate if data placement complies with location policies
        
        Args:
            location: Geographic location (eu, us, apac)
            provider: Cloud provider
            region: Cloud region
            data_classification: Data sensitivity
            
        Returns:
            (is_compliant, reason)
        """
        if location not in self.LOCATION_POLICIES:
            return True, "No location policy defined"
        
        policy = self.LOCATION_POLICIES[location]
        
        # Check provider allowed
        if provider not in policy["allowed_providers"]:
            return False, f"Provider {provider} not allowed in {location}"
        
        # Check region (if data residency required)
        if policy["data_residency"]:
            if region not in policy["allowed_regions"]:
                return False, f"Region {region} violates data residency for {location}"
        
        logger.info(f"✅ Location policy compliant: {location}/{provider}/{region}")
        return True, "Compliant"
    
    def log_access(
        self,
        user_id: str,
        user_role: str,
        action: str,
        resource_id: str,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """
        Log access attempt for audit trail
        
        Args:
            user_id: User identifier
            user_role: User's role
            action: Action attempted
            resource_id: Resource accessed
            success: Whether access was granted
            ip_address: User's IP address
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_role": user_role,
            "action": action,
            "resource_id": resource_id,
            "success": success,
            "ip_address": ip_address,
        }
        
        self.audit_log.append(audit_entry)
        
        # Keep last 10000 entries
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
        
        status = "✅ SUCCESS" if success else "❌ DENIED"
        logger.info(f"🔍 AUDIT: {status} | {user_role} | {action} | {resource_id}")
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict]:
        """
        Retrieve audit log entries
        
        Args:
            user_id: Filter by user (optional)
            hours: Number of hours to look back
            
        Returns:
            List of audit entries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_log = []
        for entry in self.audit_log:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            
            if entry_time < cutoff_time:
                continue
            
            if user_id and entry["user_id"] != user_id:
                continue
            
            filtered_log.append(entry)
        
        return filtered_log


class EncryptionService:
    """
    Data encryption service
    Provides encryption at rest and key management
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption service
        
        Args:
            master_key: Master encryption key (base64 encoded)
        """
        if master_key:
            self.master_key = master_key.encode()
        else:
            # Generate a new key
            self.master_key = Fernet.generate_key()
            logger.warning("⚠️ Generated new encryption key. Store securely!")
        
        self.fernet = Fernet(self.master_key)
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password
            salt: Salt for key derivation
            
        Returns:
            Derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt data using Fernet (AES-128)
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        try:
            encrypted = self.fernet.encrypt(data)
            logger.debug(f"🔒 Data encrypted: {len(data)} bytes -> {len(encrypted)} bytes")
            return encrypted
        except Exception as e:
            logger.error(f"❌ Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            logger.debug(f"🔓 Data decrypted: {len(encrypted_data)} bytes -> {len(decrypted)} bytes")
            return decrypted
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            raise
    
    def encrypt_file(
        self,
        data: bytes,
        data_classification: DataClassification
    ) -> Tuple[bytes, Dict[str, str]]:
        """
        Encrypt file with metadata
        
        Args:
            data: File data
            data_classification: Data sensitivity
            
        Returns:
            (encrypted_data, metadata)
        """
        encrypted = self.encrypt_data(data)
        
        metadata = {
            "encrypted": "true",
            "algorithm": "Fernet-AES128",
            "classification": data_classification.value,
            "encrypted_at": datetime.now().isoformat(),
            "original_size": str(len(data)),
            "encrypted_size": str(len(encrypted)),
        }
        
        logger.info(
            f"🔒 File encrypted: {data_classification.value} | "
            f"{len(data)} bytes -> {len(encrypted)} bytes"
        )
        
        return encrypted, metadata
    
    def decrypt_file(self, encrypted_data: bytes, metadata: Dict[str, str]) -> bytes:
        """
        Decrypt file using metadata
        
        Args:
            encrypted_data: Encrypted file data
            metadata: Encryption metadata
            
        Returns:
            Decrypted data
        """
        if metadata.get("encrypted") != "true":
            logger.warning("⚠️ File is not encrypted")
            return encrypted_data
        
        decrypted = self.decrypt_data(encrypted_data)
        
        logger.info(
            f"🔓 File decrypted: {metadata.get('classification')} | "
            f"{len(encrypted_data)} bytes -> {len(decrypted)} bytes"
        )
        
        return decrypted


class SecurityPolicyEngine:
    """
    Security policy engine that adapts to storage location
    """
    
    def __init__(
        self,
        access_control: AccessControlService,
        encryption: EncryptionService
    ):
        """Initialize policy engine"""
        self.access_control = access_control
        self.encryption = encryption
    
    def evaluate_policy(
        self,
        user_role: str,
        action: str,
        data_classification: DataClassification,
        location: str,
        provider: str,
        region: str
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate all security policies
        
        Returns:
            (allowed, reasons)
        """
        reasons = []
        
        # Check RBAC permission
        has_permission = self.access_control.check_permission(
            user_role, action, data_classification.value
        )
        
        if not has_permission:
            reasons.append(f"User role '{user_role}' lacks permission for '{action}'")
            return False, reasons
        
        # Check location policy
        location_ok, location_reason = self.access_control.validate_location_policy(
            location, provider, region, data_classification
        )
        
        if not location_ok:
            reasons.append(location_reason)
            return False, reasons
        
        # Check if encryption required
        location_policy = self.access_control.LOCATION_POLICIES.get(location, {})
        if location_policy.get("requires_encryption"):
            reasons.append("Encryption required by location policy")
        
        logger.info(f"✅ Security policy check passed: {user_role} | {action} | {location}")
        return True, reasons
    
    def apply_encryption_policy(
        self,
        data: bytes,
        data_classification: DataClassification,
        location: str
    ) -> Tuple[bytes, Dict[str, str]]:
        """
        Apply encryption based on policy
        
        Returns:
            (processed_data, metadata)
        """
        location_policy = self.access_control.LOCATION_POLICIES.get(location, {})
        
        # Check if encryption required
        if location_policy.get("requires_encryption") or \
           data_classification in [DataClassification.PII, DataClassification.PHI, DataClassification.FINANCIAL]:
            
            encrypted_data, metadata = self.encryption.encrypt_file(data, data_classification)
            metadata["encryption_policy"] = "enforced"
            return encrypted_data, metadata
        else:
            metadata = {
                "encrypted": "false",
                "classification": data_classification.value,
                "encryption_policy": "not_required"
            }
            return data, metadata


# Global instances
access_control_service = AccessControlService()
encryption_service = EncryptionService()
security_policy_engine = SecurityPolicyEngine(access_control_service, encryption_service)
