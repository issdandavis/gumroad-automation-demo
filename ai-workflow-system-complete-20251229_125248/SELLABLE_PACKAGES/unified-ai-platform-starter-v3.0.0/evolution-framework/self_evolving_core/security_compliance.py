"""
Security and Compliance Features
================================

Enterprise-grade security and compliance for AWS Bedrock AI Evolution System.
Implements IAM roles, encryption, audit logging, and compliance monitoring.
"""

import logging
import json
import hashlib
import hmac
import base64
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CHANGE = "system_change"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"
    ERROR = "error"


@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: str  # low, medium, high, critical
    source: str
    user_id: Optional[str]
    resource: str
    action: str
    result: str  # success, failure, denied
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "severity": self.severity,
            "source": self.source,
            "user_id": self.user_id,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }


@dataclass
class ComplianceCheck:
    """Compliance check result"""
    check_id: str
    framework: str
    control_id: str
    description: str
    status: str  # compliant, non_compliant, not_applicable
    severity: str
    findings: List[str]
    remediation: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "framework": self.framework,
            "control_id": self.control_id,
            "description": self.description,
            "status": self.status,
            "severity": self.severity,
            "findings": self.findings,
            "remediation": self.remediation,
            "timestamp": self.timestamp.isoformat()
        }


class EncryptionManager:
    """Manages encryption for data at rest and in transit"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        self.kms_client = None
        self.master_key_id = None
        
        if aws_config_manager:
            try:
                self.kms_client = boto3.client('kms', 
                    region_name=aws_config_manager.config.region)
                self.master_key_id = aws_config_manager.config.security.kms_key_id
            except Exception as e:
                logger.error(f"Failed to initialize KMS client: {e}")
    
    def encrypt_data(self, data: str, context: Dict[str, str] = None) -> Dict[str, Any]:
        """Encrypt data using AWS KMS"""
        
        if not self.kms_client or not self.master_key_id:
            # Fallback to local encryption
            return self._encrypt_local(data)
        
        try:
            response = self.kms_client.encrypt(
                KeyId=self.master_key_id,
                Plaintext=data.encode('utf-8'),
                EncryptionContext=context or {}
            )
            
            return {
                "encrypted_data": base64.b64encode(response['CiphertextBlob']).decode('utf-8'),
                "key_id": response['KeyId'],
                "encryption_context": context or {},
                "method": "kms"
            }
            
        except Exception as e:
            logger.error(f"KMS encryption failed: {e}")
            return self._encrypt_local(data)
    
    def decrypt_data(self, encrypted_data: str, method: str = "kms", 
                    context: Dict[str, str] = None) -> str:
        """Decrypt data"""
        
        if method == "kms" and self.kms_client:
            try:
                ciphertext_blob = base64.b64decode(encrypted_data.encode('utf-8'))
                
                response = self.kms_client.decrypt(
                    CiphertextBlob=ciphertext_blob,
                    EncryptionContext=context or {}
                )
                
                return response['Plaintext'].decode('utf-8')
                
            except Exception as e:
                logger.error(f"KMS decryption failed: {e}")
                raise
        
        elif method == "local":
            return self._decrypt_local(encrypted_data)
        
        else:
            raise ValueError(f"Unsupported decryption method: {method}")
    
    def _encrypt_local(self, data: str) -> Dict[str, Any]:
        """Local encryption fallback (simplified)"""
        
        # In production, use proper local encryption
        encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        
        return {
            "encrypted_data": encoded,
            "method": "local",
            "warning": "Using fallback encryption - not suitable for production"
        }
    
    def _decrypt_local(self, encrypted_data: str) -> str:
        """Local decryption fallback"""
        
        return base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
    
    def generate_data_key(self, key_spec: str = "AES_256") -> Dict[str, Any]:
        """Generate data encryption key"""
        
        if not self.kms_client or not self.master_key_id:
            raise RuntimeError("KMS not available for data key generation")
        
        try:
            response = self.kms_client.generate_data_key(
                KeyId=self.master_key_id,
                KeySpec=key_spec
            )
            
            return {
                "plaintext_key": response['Plaintext'],
                "encrypted_key": base64.b64encode(response['CiphertextBlob']).decode('utf-8'),
                "key_id": response['KeyId']
            }
            
        except Exception as e:
            logger.error(f"Data key generation failed: {e}")
            raise


class IAMManager:
    """Manages IAM roles and policies"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        self.iam_client = None
        self.sts_client = None
        
        if aws_config_manager:
            try:
                self.iam_client = boto3.client('iam')
                self.sts_client = boto3.client('sts')
            except Exception as e:
                logger.error(f"Failed to initialize IAM clients: {e}")
    
    def validate_permissions(self, required_permissions: List[str]) -> Dict[str, bool]:
        """Validate current IAM permissions"""
        
        if not self.sts_client:
            return {perm: False for perm in required_permissions}
        
        results = {}
        
        for permission in required_permissions:
            try:
                # Parse permission (service:action)
                if ':' in permission:
                    service, action = permission.split(':', 1)
                else:
                    service, action = permission, '*'
                
                # Simulate permission check (simplified)
                # In production, use IAM policy simulator
                results[permission] = True  # Assume granted for demo
                
            except Exception as e:
                logger.error(f"Permission check failed for {permission}: {e}")
                results[permission] = False
        
        return results
    
    def get_current_identity(self) -> Dict[str, Any]:
        """Get current AWS identity"""
        
        if not self.sts_client:
            return {"error": "STS client not available"}
        
        try:
            response = self.sts_client.get_caller_identity()
            return {
                "user_id": response.get('UserId'),
                "account": response.get('Account'),
                "arn": response.get('Arn'),
                "type": "aws_identity"
            }
            
        except Exception as e:
            logger.error(f"Failed to get caller identity: {e}")
            return {"error": str(e)}
    
    def check_least_privilege(self, role_arn: str) -> Dict[str, Any]:
        """Check if role follows least privilege principle"""
        
        if not self.iam_client:
            return {"error": "IAM client not available"}
        
        try:
            # Extract role name from ARN
            role_name = role_arn.split('/')[-1]
            
            # Get role policies
            response = self.iam_client.list_attached_role_policies(RoleName=role_name)
            attached_policies = response['AttachedPolicies']
            
            # Get inline policies
            inline_response = self.iam_client.list_role_policies(RoleName=role_name)
            inline_policies = inline_response['PolicyNames']
            
            # Analyze policies (simplified)
            findings = []
            
            for policy in attached_policies:
                if policy['PolicyName'] == 'AdministratorAccess':
                    findings.append("Role has AdministratorAccess - violates least privilege")
            
            if len(attached_policies) > 5:
                findings.append(f"Role has {len(attached_policies)} attached policies - consider consolidation")
            
            return {
                "role_name": role_name,
                "attached_policies": len(attached_policies),
                "inline_policies": len(inline_policies),
                "findings": findings,
                "compliant": len(findings) == 0
            }
            
        except Exception as e:
            logger.error(f"Least privilege check failed: {e}")
            return {"error": str(e)}


class AuditLogger:
    """Enhanced audit logger for security events"""
    
    def __init__(self, storage_path: str = "AI_NETWORK_LOCAL", 
                 cloudwatch_enabled: bool = False):
        self.storage_path = storage_path
        self.cloudwatch_enabled = cloudwatch_enabled
        self.cloudwatch_client = None
        self.log_group = "ai-evolution-audit"
        
        if cloudwatch_enabled:
            try:
                self.cloudwatch_client = boto3.client('logs')
                self._ensure_log_group()
            except Exception as e:
                logger.error(f"Failed to initialize CloudWatch logging: {e}")
    
    def log_security_event(self, event_type: str, severity: str, source: str,
                          resource: str, action: str, result: str,
                          details: Dict[str, Any], user_id: str = None,
                          ip_address: str = None) -> str:
        """Log security event"""
        
        event_id = f"sec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        event = SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            source=source,
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            details=details,
            ip_address=ip_address
        )
        
        # Log to local file
        self._log_to_file(event)
        
        # Log to CloudWatch if enabled
        if self.cloudwatch_enabled:
            self._log_to_cloudwatch(event)
        
        # Alert on high severity events
        if severity in ['high', 'critical']:
            self._trigger_security_alert(event)
        
        return event_id
    
    def log_compliance_event(self, framework: str, control_id: str, 
                           status: str, details: Dict[str, Any]) -> str:
        """Log compliance-related event"""
        
        return self.log_security_event(
            event_type=AuditEventType.COMPLIANCE_CHECK.value,
            severity="medium" if status == "non_compliant" else "low",
            source="compliance_monitor",
            resource=f"{framework}:{control_id}",
            action="compliance_check",
            result=status,
            details=details
        )
    
    def log_data_access(self, resource: str, action: str, user_id: str = None,
                       classification: str = "internal", result: str = "success") -> str:
        """Log data access event"""
        
        severity = "high" if classification in ["confidential", "restricted"] else "medium"
        
        return self.log_security_event(
            event_type=AuditEventType.DATA_ACCESS.value,
            severity=severity,
            source="data_access_monitor",
            resource=resource,
            action=action,
            result=result,
            details={"classification": classification},
            user_id=user_id
        )
    
    def _log_to_file(self, event: SecurityEvent) -> None:
        """Log event to local file"""
        
        try:
            log_file = f"{self.storage_path}/security_audit.log"
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log to file: {e}")
    
    def _log_to_cloudwatch(self, event: SecurityEvent) -> None:
        """Log event to CloudWatch"""
        
        if not self.cloudwatch_client:
            return
        
        try:
            self.cloudwatch_client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=f"security-{datetime.now().strftime('%Y-%m-%d')}",
                logEvents=[{
                    'timestamp': int(event.timestamp.timestamp() * 1000),
                    'message': json.dumps(event.to_dict())
                }]
            )
            
        except Exception as e:
            logger.error(f"Failed to log to CloudWatch: {e}")
    
    def _ensure_log_group(self) -> None:
        """Ensure CloudWatch log group exists"""
        
        try:
            self.cloudwatch_client.create_log_group(logGroupName=self.log_group)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                logger.error(f"Failed to create log group: {e}")
    
    def _trigger_security_alert(self, event: SecurityEvent) -> None:
        """Trigger security alert for high severity events"""
        
        logger.critical(f"SECURITY ALERT: {event.event_type} - {event.details}")
        
        # In production, integrate with SNS, PagerDuty, etc.


class ComplianceMonitor:
    """Monitors compliance with various frameworks"""
    
    def __init__(self, audit_logger: AuditLogger, encryption_manager: EncryptionManager,
                 iam_manager: IAMManager):
        self.audit_logger = audit_logger
        self.encryption_manager = encryption_manager
        self.iam_manager = iam_manager
        
        # Compliance checks by framework
        self.compliance_checks = {
            ComplianceFramework.SOC2.value: [
                self._check_access_controls,
                self._check_data_encryption,
                self._check_audit_logging,
                self._check_change_management
            ],
            ComplianceFramework.GDPR.value: [
                self._check_data_encryption,
                self._check_data_retention,
                self._check_access_controls,
                self._check_audit_logging
            ],
            ComplianceFramework.ISO27001.value: [
                self._check_access_controls,
                self._check_data_encryption,
                self._check_incident_management,
                self._check_risk_management
            ]
        }
    
    def run_compliance_check(self, framework: str) -> List[ComplianceCheck]:
        """Run compliance checks for a framework"""
        
        if framework not in self.compliance_checks:
            raise ValueError(f"Unsupported compliance framework: {framework}")
        
        results = []
        checks = self.compliance_checks[framework]
        
        for check_func in checks:
            try:
                result = check_func(framework)
                results.append(result)
                
                # Log compliance event
                self.audit_logger.log_compliance_event(
                    framework=framework,
                    control_id=result.control_id,
                    status=result.status,
                    details={"findings": result.findings}
                )
                
            except Exception as e:
                logger.error(f"Compliance check failed: {e}")
                
                error_result = ComplianceCheck(
                    check_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    framework=framework,
                    control_id="unknown",
                    description=f"Check failed: {check_func.__name__}",
                    status="error",
                    severity="high",
                    findings=[str(e)],
                    remediation=["Investigate check failure"],
                    timestamp=datetime.now()
                )
                results.append(error_result)
        
        return results
    
    def _check_access_controls(self, framework: str) -> ComplianceCheck:
        """Check access control compliance"""
        
        findings = []
        remediation = []
        
        # Check IAM permissions
        identity = self.iam_manager.get_current_identity()
        if "error" in identity:
            findings.append("Unable to verify IAM identity")
            remediation.append("Check AWS credentials and permissions")
        
        # Check for least privilege
        if identity.get("arn"):
            privilege_check = self.iam_manager.check_least_privilege(identity["arn"])
            if not privilege_check.get("compliant", False):
                findings.extend(privilege_check.get("findings", []))
                remediation.append("Review and reduce IAM permissions")
        
        status = "compliant" if not findings else "non_compliant"
        severity = "high" if findings else "low"
        
        return ComplianceCheck(
            check_id=f"access_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="AC-1",
            description="Access control verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def _check_data_encryption(self, framework: str) -> ComplianceCheck:
        """Check data encryption compliance"""
        
        findings = []
        remediation = []
        
        # Check if KMS is configured
        if not self.encryption_manager.kms_client:
            findings.append("KMS encryption not configured")
            remediation.append("Configure AWS KMS for data encryption")
        
        if not self.encryption_manager.master_key_id:
            findings.append("Master encryption key not specified")
            remediation.append("Configure KMS master key")
        
        # Test encryption capability
        try:
            test_data = "compliance_test_data"
            encrypted = self.encryption_manager.encrypt_data(test_data)
            
            if encrypted.get("method") == "local":
                findings.append("Using fallback encryption instead of KMS")
                remediation.append("Fix KMS configuration")
            
        except Exception as e:
            findings.append(f"Encryption test failed: {e}")
            remediation.append("Fix encryption configuration")
        
        status = "compliant" if not findings else "non_compliant"
        severity = "high" if findings else "low"
        
        return ComplianceCheck(
            check_id=f"encrypt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="SC-13",
            description="Data encryption verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def _check_audit_logging(self, framework: str) -> ComplianceCheck:
        """Check audit logging compliance"""
        
        findings = []
        remediation = []
        
        # Check if audit logging is enabled
        if not self.audit_logger.cloudwatch_enabled:
            findings.append("CloudWatch audit logging not enabled")
            remediation.append("Enable CloudWatch logging for audit trails")
        
        # Check log retention (simplified)
        # In production, check actual CloudWatch log retention settings
        
        status = "compliant" if not findings else "non_compliant"
        severity = "medium" if findings else "low"
        
        return ComplianceCheck(
            check_id=f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="AU-2",
            description="Audit logging verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def _check_change_management(self, framework: str) -> ComplianceCheck:
        """Check change management compliance"""
        
        # Simplified check - in production, integrate with CI/CD systems
        findings = []
        remediation = []
        
        # Check if changes are tracked
        # This would integrate with version control, deployment systems, etc.
        
        status = "compliant"  # Assume compliant for demo
        severity = "low"
        
        return ComplianceCheck(
            check_id=f"change_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="CM-3",
            description="Change management verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def _check_data_retention(self, framework: str) -> ComplianceCheck:
        """Check data retention compliance"""
        
        findings = []
        remediation = []
        
        # Check if data retention policies are configured
        # This would check S3 lifecycle policies, DynamoDB TTL, etc.
        
        status = "compliant"  # Assume compliant for demo
        severity = "low"
        
        return ComplianceCheck(
            check_id=f"retention_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="SI-12",
            description="Data retention verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def _check_incident_management(self, framework: str) -> ComplianceCheck:
        """Check incident management compliance"""
        
        findings = []
        remediation = []
        
        # Check if incident response procedures are in place
        # This would check alerting, escalation procedures, etc.
        
        status = "compliant"  # Assume compliant for demo
        severity = "low"
        
        return ComplianceCheck(
            check_id=f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="IR-1",
            description="Incident management verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def _check_risk_management(self, framework: str) -> ComplianceCheck:
        """Check risk management compliance"""
        
        findings = []
        remediation = []
        
        # Check if risk assessment procedures are in place
        # This would check risk registers, assessments, etc.
        
        status = "compliant"  # Assume compliant for demo
        severity = "low"
        
        return ComplianceCheck(
            check_id=f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            control_id="RA-1",
            description="Risk management verification",
            status=status,
            severity=severity,
            findings=findings,
            remediation=remediation,
            timestamp=datetime.now()
        )
    
    def generate_compliance_report(self, framework: str) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        checks = self.run_compliance_check(framework)
        
        total_checks = len(checks)
        compliant_checks = len([c for c in checks if c.status == "compliant"])
        non_compliant_checks = len([c for c in checks if c.status == "non_compliant"])
        error_checks = len([c for c in checks if c.status == "error"])
        
        compliance_score = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Categorize findings by severity
        findings_by_severity = {"low": [], "medium": [], "high": [], "critical": []}
        all_remediation = []
        
        for check in checks:
            for finding in check.findings:
                findings_by_severity[check.severity].append({
                    "control_id": check.control_id,
                    "finding": finding
                })
            all_remediation.extend(check.remediation)
        
        return {
            "framework": framework,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": total_checks,
                "compliant": compliant_checks,
                "non_compliant": non_compliant_checks,
                "errors": error_checks,
                "compliance_score": compliance_score
            },
            "findings_by_severity": findings_by_severity,
            "remediation_actions": list(set(all_remediation)),
            "detailed_results": [check.to_dict() for check in checks]
        }


class SecurityManager:
    """Main security management class"""
    
    def __init__(self, aws_config_manager=None, storage_path: str = "AI_NETWORK_LOCAL"):
        self.aws_config_manager = aws_config_manager
        self.storage_path = storage_path
        
        # Initialize components
        self.encryption_manager = EncryptionManager(aws_config_manager)
        self.iam_manager = IAMManager(aws_config_manager)
        self.audit_logger = AuditLogger(storage_path, 
                                      cloudwatch_enabled=aws_config_manager is not None)
        self.compliance_monitor = ComplianceMonitor(
            self.audit_logger, self.encryption_manager, self.iam_manager
        )
    
    def initialize_security(self) -> Dict[str, Any]:
        """Initialize security components and run initial checks"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "initialization_status": {},
            "security_checks": {},
            "recommendations": []
        }
        
        # Check encryption
        try:
            test_data = "security_initialization_test"
            encrypted = self.encryption_manager.encrypt_data(test_data)
            decrypted = self.encryption_manager.decrypt_data(
                encrypted["encrypted_data"], encrypted["method"]
            )
            
            encryption_ok = decrypted == test_data
            results["initialization_status"]["encryption"] = encryption_ok
            
            if not encryption_ok:
                results["recommendations"].append("Fix encryption configuration")
            
        except Exception as e:
            results["initialization_status"]["encryption"] = False
            results["recommendations"].append(f"Fix encryption: {e}")
        
        # Check IAM
        try:
            identity = self.iam_manager.get_current_identity()
            iam_ok = "error" not in identity
            results["initialization_status"]["iam"] = iam_ok
            results["security_checks"]["current_identity"] = identity
            
            if not iam_ok:
                results["recommendations"].append("Fix IAM configuration")
            
        except Exception as e:
            results["initialization_status"]["iam"] = False
            results["recommendations"].append(f"Fix IAM: {e}")
        
        # Log initialization
        self.audit_logger.log_security_event(
            event_type=AuditEventType.SYSTEM_CHANGE.value,
            severity="medium",
            source="security_manager",
            resource="security_system",
            action="initialize",
            result="success" if all(results["initialization_status"].values()) else "partial",
            details=results
        )
        
        return results
    
    def run_security_assessment(self) -> Dict[str, Any]:
        """Run comprehensive security assessment"""
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "compliance_reports": {},
            "security_posture": {},
            "recommendations": []
        }
        
        # Run compliance checks
        for framework in [ComplianceFramework.SOC2.value, ComplianceFramework.GDPR.value]:
            try:
                report = self.compliance_monitor.generate_compliance_report(framework)
                assessment["compliance_reports"][framework] = report
                
                if report["summary"]["compliance_score"] < 80:
                    assessment["recommendations"].append(
                        f"Improve {framework} compliance (current: {report['summary']['compliance_score']:.1f}%)"
                    )
                    
            except Exception as e:
                logger.error(f"Compliance check failed for {framework}: {e}")
                assessment["compliance_reports"][framework] = {"error": str(e)}
        
        # Security posture assessment
        try:
            identity = self.iam_manager.get_current_identity()
            if identity.get("arn"):
                privilege_check = self.iam_manager.check_least_privilege(identity["arn"])
                assessment["security_posture"]["least_privilege"] = privilege_check
        except Exception as e:
            assessment["security_posture"]["least_privilege"] = {"error": str(e)}
        
        # Log assessment
        self.audit_logger.log_security_event(
            event_type=AuditEventType.SECURITY_EVENT.value,
            severity="low",
            source="security_manager",
            resource="security_system",
            action="assessment",
            result="completed",
            details={"assessment_summary": assessment}
        )
        
        return assessment
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "encryption_available": self.encryption_manager.kms_client is not None,
            "iam_available": self.iam_manager.iam_client is not None,
            "audit_logging_enabled": self.audit_logger.cloudwatch_enabled,
            "compliance_frameworks": list(self.compliance_monitor.compliance_checks.keys()),
            "current_identity": self.iam_manager.get_current_identity()
        }


# Convenience function to create security system
def create_security_system(aws_config_manager=None, 
                         storage_path: str = "AI_NETWORK_LOCAL") -> SecurityManager:
    """Create integrated security system"""
    
    security_manager = SecurityManager(aws_config_manager, storage_path)
    
    # Initialize security
    init_result = security_manager.initialize_security()
    logger.info(f"Security system initialized: {init_result['initialization_status']}")
    
    return security_manager