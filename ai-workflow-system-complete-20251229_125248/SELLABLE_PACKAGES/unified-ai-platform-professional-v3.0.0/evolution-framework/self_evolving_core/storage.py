"""
Storage Synchronization for Self-Evolving AI Framework
======================================================

Multi-platform distributed storage with:
- Local, Dropbox, GitHub, Notion, S3 support
- Retry with exponential backoff and jitter
- Integrity verification via checksums
- Conflict resolution
- Circuit breaker pattern for resilience
"""

import os
import json
import hashlib
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import requests

from .models import SyncResult, StoragePlatform

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker for resilient API calls"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0
    half_open_calls: int = 0
    
    def can_execute(self) -> bool:
        """Check if request can proceed"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        else:  # HALF_OPEN
            return self.half_open_calls < self.half_open_max_calls
    
    def record_success(self) -> None:
        """Record successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0
    
    def record_failure(self) -> None:
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


@dataclass
class SyncOperation:
    """Queued sync operation"""
    id: str
    platform: str
    operation: str  # upload, download, delete
    path: str
    data: Optional[Dict[str, Any]] = None
    checksum: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_attempt: Optional[str] = None
    error: Optional[str] = None


class SyncQueue:
    """
    Queue for failed sync operations with retry logic.
    
    Features:
    - Exponential backoff with jitter
    - Max retry limits
    - Priority ordering
    """
    
    def __init__(self, max_backoff: float = 300.0, base_backoff: float = 2.0):
        self.queue: Dict[str, SyncOperation] = {}
        self.max_backoff = max_backoff
        self.base_backoff = base_backoff
    
    def add(self, operation: SyncOperation) -> None:
        """Add operation to queue"""
        self.queue[operation.id] = operation
        logger.debug(f"Queued sync operation: {operation.id}")
    
    def get_pending(self) -> List[SyncOperation]:
        """Get operations ready for retry"""
        now = datetime.now()
        pending = []
        
        for op in self.queue.values():
            if op.attempts >= op.max_attempts:
                continue
            
            if op.last_attempt:
                last = datetime.fromisoformat(op.last_attempt)
                backoff = self.calculate_backoff(op.attempts)
                if (now - last).total_seconds() < backoff:
                    continue
            
            pending.append(op)
        
        return sorted(pending, key=lambda x: x.attempts)
    
    def mark_complete(self, operation_id: str) -> None:
        """Remove completed operation from queue"""
        if operation_id in self.queue:
            del self.queue[operation_id]
            logger.debug(f"Completed sync operation: {operation_id}")
    
    def mark_attempted(self, operation_id: str, error: Optional[str] = None) -> None:
        """Record retry attempt"""
        if operation_id in self.queue:
            op = self.queue[operation_id]
            op.attempts += 1
            op.last_attempt = datetime.now().isoformat()
            op.error = error
    
    def calculate_backoff(self, attempts: int) -> float:
        """
        Exponential backoff with jitter.
        Formula: min(max_backoff, base^attempts) + random_jitter
        """
        backoff = min(self.max_backoff, self.base_backoff ** attempts)
        jitter = random.uniform(0, backoff * 0.1)
        return backoff + jitter
    
    def get_failed(self) -> List[SyncOperation]:
        """Get operations that exceeded max attempts"""
        return [op for op in self.queue.values() if op.attempts >= op.max_attempts]
    
    def clear_failed(self) -> int:
        """Remove failed operations, return count"""
        failed_ids = [op.id for op in self.get_failed()]
        for op_id in failed_ids:
            del self.queue[op_id]
        return len(failed_ids)


class LocalStorage:
    """Local file system storage"""
    
    def __init__(self, base_path: str = "AI_NETWORK_LOCAL"):
        self.base_path = Path(base_path)
        self._setup_structure()
    
    def _setup_structure(self) -> None:
        """Create directory structure"""
        directories = [
            "messages/inbox",
            "messages/outbox",
            "messages/archive",
            "ai_registry",
            "evolution_logs",
            "network_state",
            "shared_knowledge",
            "backups",
            "snapshots",
            "plugins"
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
    
    def save(self, path: str, data: Dict[str, Any]) -> SyncResult:
        """Save data to local file"""
        try:
            full_path = self.base_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = json.dumps(data, indent=2, default=str)
            checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            return SyncResult(
                success=True,
                platform="local",
                operation="upload",
                path=path,
                checksum=checksum
            )
        except Exception as e:
            logger.error(f"Local save failed: {e}")
            return SyncResult(
                success=False,
                platform="local",
                operation="upload",
                path=path,
                error=str(e)
            )
    
    def load(self, path: str) -> Optional[Dict[str, Any]]:
        """Load data from local file"""
        try:
            full_path = self.base_path / path
            if not full_path.exists():
                return None
            
            with open(full_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Local load failed: {e}")
            return None
    
    def delete(self, path: str) -> SyncResult:
        """Delete local file"""
        try:
            full_path = self.base_path / path
            if full_path.exists():
                full_path.unlink()
            
            return SyncResult(
                success=True,
                platform="local",
                operation="delete",
                path=path
            )
        except Exception as e:
            return SyncResult(
                success=False,
                platform="local",
                operation="delete",
                path=path,
                error=str(e)
            )
    
    def list_files(self, directory: str = "") -> List[str]:
        """List files in directory"""
        try:
            dir_path = self.base_path / directory
            if not dir_path.exists():
                return []
            return [str(f.relative_to(self.base_path)) for f in dir_path.rglob("*") if f.is_file()]
        except Exception as e:
            logger.error(f"Local list failed: {e}")
            return []


class DropboxClient:
    """Dropbox storage client with circuit breaker"""
    
    def __init__(self, access_token: str = "", app_folder: str = "/AI_Network"):
        self.access_token = access_token or os.getenv("DROPBOX_ACCESS_TOKEN", "")
        self.app_folder = app_folder
        self.api_url = "https://api.dropboxapi.com/2"
        self.content_url = "https://content.dropboxapi.com/2"
        self.circuit = CircuitBreaker()
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        return bool(self.access_token)
    
    def upload(self, path: str, data: Dict[str, Any]) -> SyncResult:
        """Upload data to Dropbox"""
        if not self.is_configured():
            return SyncResult(
                success=False,
                platform="dropbox",
                operation="upload",
                path=path,
                error="Dropbox not configured"
            )
        
        if not self.circuit.can_execute():
            return SyncResult(
                success=False,
                platform="dropbox",
                operation="upload",
                path=path,
                error="Circuit breaker open"
            )
        
        try:
            content = json.dumps(data, indent=2, default=str)
            checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": json.dumps({
                    "path": f"{self.app_folder}/{path}",
                    "mode": "overwrite"
                })
            }
            
            response = requests.post(
                f"{self.content_url}/files/upload",
                headers=headers,
                data=content.encode(),
                timeout=30
            )
            
            if response.status_code == 200:
                self.circuit.record_success()
                return SyncResult(
                    success=True,
                    platform="dropbox",
                    operation="upload",
                    path=path,
                    checksum=checksum
                )
            else:
                self.circuit.record_failure()
                return SyncResult(
                    success=False,
                    platform="dropbox",
                    operation="upload",
                    path=path,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.circuit.record_failure()
            logger.error(f"Dropbox upload failed: {e}")
            return SyncResult(
                success=False,
                platform="dropbox",
                operation="upload",
                path=path,
                error=str(e)
            )
    
    def download(self, path: str) -> Optional[Dict[str, Any]]:
        """Download data from Dropbox"""
        if not self.is_configured() or not self.circuit.can_execute():
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Dropbox-API-Arg": json.dumps({"path": f"{self.app_folder}/{path}"})
            }
            
            response = requests.post(
                f"{self.content_url}/files/download",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.circuit.record_success()
                return json.loads(response.content)
            else:
                self.circuit.record_failure()
                return None
                
        except Exception as e:
            self.circuit.record_failure()
            logger.error(f"Dropbox download failed: {e}")
            return None


class GitHubClient:
    """GitHub storage client for version-controlled data"""
    
    def __init__(self, token: str = "", repo: str = "", owner: str = ""):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.repo = repo or os.getenv("GITHUB_REPO", "ai-evolution-hub")
        self.owner = owner or os.getenv("GITHUB_OWNER", "")
        self.api_url = "https://api.github.com"
        self.circuit = CircuitBreaker()
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def is_configured(self) -> bool:
        return bool(self.token and self.owner)
    
    def upload(self, path: str, data: Dict[str, Any], message: str = "Auto-sync") -> SyncResult:
        """Upload/update file in GitHub repo"""
        if not self.is_configured():
            return SyncResult(
                success=False,
                platform="github",
                operation="upload",
                path=path,
                error="GitHub not configured"
            )
        
        if not self.circuit.can_execute():
            return SyncResult(
                success=False,
                platform="github",
                operation="upload",
                path=path,
                error="Circuit breaker open"
            )
        
        try:
            import base64
            content = json.dumps(data, indent=2, default=str)
            checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
            encoded = base64.b64encode(content.encode()).decode()
            
            url = f"{self.api_url}/repos/{self.owner}/{self.repo}/contents/{path}"
            
            # Check if file exists to get SHA
            sha = None
            response = requests.get(url, headers=self._headers(), timeout=30)
            if response.status_code == 200:
                sha = response.json().get("sha")
            
            # Create/update file
            payload = {
                "message": message,
                "content": encoded
            }
            if sha:
                payload["sha"] = sha
            
            response = requests.put(url, headers=self._headers(), json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                self.circuit.record_success()
                return SyncResult(
                    success=True,
                    platform="github",
                    operation="upload",
                    path=path,
                    checksum=checksum
                )
            else:
                self.circuit.record_failure()
                return SyncResult(
                    success=False,
                    platform="github",
                    operation="upload",
                    path=path,
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.circuit.record_failure()
            logger.error(f"GitHub upload failed: {e}")
            return SyncResult(
                success=False,
                platform="github",
                operation="upload",
                path=path,
                error=str(e)
            )


class StorageSync:
    """
    Multi-platform storage synchronization.
    
    Features:
    - Sync to multiple platforms simultaneously
    - Automatic retry with queue
    - Integrity verification
    - Conflict resolution
    """
    
    def __init__(self, config=None):
        self.local = LocalStorage(config.local_path if config else "AI_NETWORK_LOCAL")
        self.dropbox = DropboxClient(
            config.dropbox_token if config else "",
            config.dropbox_app_folder if config else "/AI_Network"
        )
        self.github = GitHubClient(
            config.github_token if config else "",
            config.github_repo if config else "",
            config.github_owner if config else ""
        )
        self.queue = SyncQueue()
        
        self.platforms = {
            "local": self.local,
            "dropbox": self.dropbox,
            "github": self.github
        }
    
    def sync_all(self, data: Dict[str, Any], path: str, 
                 platforms: Optional[List[str]] = None) -> Dict[str, SyncResult]:
        """
        Sync data to all specified platforms.
        
        Args:
            data: Data to sync
            path: File path
            platforms: List of platforms (default: all configured)
            
        Returns:
            Dict mapping platform name to SyncResult
        """
        if platforms is None:
            platforms = ["local"]
            if self.dropbox.is_configured():
                platforms.append("dropbox")
            if self.github.is_configured():
                platforms.append("github")
        
        results = {}
        checksum = hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        
        for platform in platforms:
            if platform == "local":
                results[platform] = self.local.save(path, data)
            elif platform == "dropbox":
                results[platform] = self.dropbox.upload(path, data)
            elif platform == "github":
                results[platform] = self.github.upload(path, data)
            else:
                results[platform] = SyncResult(
                    success=False,
                    platform=platform,
                    operation="upload",
                    path=path,
                    error=f"Unknown platform: {platform}"
                )
            
            # Queue failed operations for retry
            if not results[platform].success:
                op = SyncOperation(
                    id=f"sync_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    platform=platform,
                    operation="upload",
                    path=path,
                    data=data,
                    checksum=checksum
                )
                self.queue.add(op)
        
        return results
    
    def process_queue(self) -> List[SyncResult]:
        """Process queued operations with retry"""
        results = []
        pending = self.queue.get_pending()
        
        for op in pending:
            if op.platform == "local":
                result = self.local.save(op.path, op.data)
            elif op.platform == "dropbox":
                result = self.dropbox.upload(op.path, op.data)
            elif op.platform == "github":
                result = self.github.upload(op.path, op.data)
            else:
                continue
            
            result.retry_count = op.attempts + 1
            results.append(result)
            
            if result.success:
                self.queue.mark_complete(op.id)
            else:
                self.queue.mark_attempted(op.id, result.error)
        
        return results
    
    def verify_integrity(self, data: Dict[str, Any], expected_checksum: str) -> bool:
        """Verify data integrity using checksum"""
        actual = hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        return actual == expected_checksum
    
    def resolve_conflict(self, local_data: Dict[str, Any], 
                        remote_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve sync conflicts using timestamp-based resolution.
        
        Strategy: Most recent timestamp wins
        """
        local_time = local_data.get("_last_modified", "")
        remote_time = remote_data.get("_last_modified", "")
        
        if local_time >= remote_time:
            return local_data
        else:
            return remote_data
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "queue_size": len(self.queue.queue),
            "pending_retries": len(self.queue.get_pending()),
            "failed_operations": len(self.queue.get_failed()),
            "platforms": {
                "local": True,
                "dropbox": self.dropbox.is_configured(),
                "github": self.github.is_configured()
            },
            "circuit_breakers": {
                "dropbox": self.dropbox.circuit.state.value,
                "github": self.github.circuit.state.value
            }
        }
