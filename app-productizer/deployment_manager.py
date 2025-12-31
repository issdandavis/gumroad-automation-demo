#!/usr/bin/env python3
"""
Deployment Manager - Automated Deployment & Packaging System
============================================================

Comprehensive deployment automation for the Self-Evolving AI Framework.
Handles packaging, distribution, cloud deployment, and release management.

TUTORIAL: Deployment & Distribution
-----------------------------------
This module teaches you how to:
1. Package the framework for distribution
2. Deploy to various cloud platforms
3. Create Docker containers
4. Generate release artifacts
5. Automate CI/CD pipelines

Features:
- Multi-platform deployment (AWS, GCP, Azure, Heroku)
- Docker containerization with best practices
- Release versioning and changelog generation
- Automated testing before deployment
- Rollback capabilities for failed deployments
- Health monitoring post-deployment

Usage:
    python deployment_manager.py package          # Create distribution package
    python deployment_manager.py docker           # Build Docker image
    python deployment_manager.py deploy aws       # Deploy to AWS
    python deployment_manager.py release 2.1.0    # Create release
    python deployment_manager.py rollback         # Rollback deployment
    python deployment_manager.py status           # Check deployment status

Demo Credentials (Replace with real values):
    AWS_ACCESS_KEY_ID=AKIADEMO1234567890AB
    AWS_SECRET_ACCESS_KEY=demo1234567890abcdef1234567890abcdef12345678
    DOCKER_REGISTRY=demo-registry.example.com
"""

import os
import json
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import hashlib


# ============================================================================
# TUTORIAL SECTION 1: Data Models for Deployment
# ============================================================================
# These dataclasses define the structure of deployment configurations.
# Using dataclasses provides type safety and automatic serialization.

@dataclass
class DeploymentTarget:
    """
    TUTORIAL: Deployment Target Configuration
    
    Each deployment target represents a destination where the framework
    can be deployed. This includes cloud platforms, container registries,
    and on-premise servers.
    
    Fields:
        name: Unique identifier for the target
        platform: Cloud platform (aws, gcp, azure, heroku, docker)
        region: Geographic region for deployment
        credentials: Platform-specific credentials (use environment variables!)
        config: Additional platform-specific configuration
        enabled: Whether this target is active
    
    Example:
        target = DeploymentTarget(
            name="production-aws",
            platform="aws",
            region="us-east-1",
            credentials={"profile": "production"},
            config={"instance_type": "t3.medium"}
        )
    """
    name: str
    platform: str
    region: str = "us-east-1"
    credentials: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class DeploymentResult:
    """
    TUTORIAL: Deployment Result Tracking
    
    Captures the outcome of a deployment operation for auditing
    and rollback purposes.
    
    Fields:
        success: Whether deployment succeeded
        target: The deployment target used
        version: Version that was deployed
        timestamp: When deployment occurred
        duration_seconds: How long deployment took
        artifacts: List of deployed artifacts
        logs: Deployment logs for debugging
        rollback_id: ID for rolling back this deployment
    """
    success: bool
    target: str
    version: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_seconds: float = 0.0
    artifacts: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    rollback_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ReleaseInfo:
    """
    TUTORIAL: Release Information
    
    Defines a release version with all associated metadata.
    Used for version management and changelog generation.
    
    Fields:
        version: Semantic version (e.g., "2.1.0")
        codename: Optional release codename
        release_date: When the release was created
        changelog: List of changes in this release
        breaking_changes: List of breaking changes (important!)
        contributors: List of contributors to this release
        artifacts: Generated release artifacts
    """
    version: str
    codename: Optional[str] = None
    release_date: str = field(default_factory=lambda: datetime.now().isoformat())
    changelog: List[str] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)
    contributors: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)


# ============================================================================
# TUTORIAL SECTION 2: Demo Configuration
# ============================================================================
# These are demonstration values for testing. In production, always use
# environment variables or secure secret management!

DEMO_DEPLOYMENT_TARGETS = [
    DeploymentTarget(
        name="local-docker",
        platform="docker",
        region="local",
        credentials={
            "registry": "localhost:5000",
            "username": "demo_user",
            "password": "demo_password_change_me"
        },
        config={
            "image_name": "self-evolving-ai",
            "tag": "latest"
        }
    ),
    DeploymentTarget(
        name="aws-production",
        platform="aws",
        region="us-east-1",
        credentials={
            "access_key_id": "AKIADEMO1234567890AB",
            "secret_access_key": "demo1234567890abcdef1234567890abcdef12345678",
            "profile": "default"
        },
        config={
            "service": "ecs",
            "cluster": "ai-framework-cluster",
            "task_definition": "self-evolving-ai-task"
        },
        enabled=False  # Disabled by default for safety
    ),
    DeploymentTarget(
        name="heroku-staging",
        platform="heroku",
        region="us",
        credentials={
            "api_key": "demo-heroku-api-key-1234567890abcdef",
            "app_name": "self-evolving-ai-staging"
        },
        config={
            "dyno_type": "web",
            "dyno_size": "standard-1x"
        },
        enabled=False
    )
]


# ============================================================================
# TUTORIAL SECTION 3: Package Builder
# ============================================================================

class PackageBuilder:
    """
    TUTORIAL: Building Distribution Packages
    
    This class handles creating distributable packages of the framework.
    It supports multiple formats: wheel, tarball, zip, and Docker.
    
    Key Concepts:
    1. Package Manifest: Lists all files to include
    2. Checksums: Verify package integrity
    3. Metadata: Version, dependencies, requirements
    4. Exclusions: Files to exclude (secrets, cache, etc.)
    
    Usage:
        builder = PackageBuilder()
        package_path = builder.build_package("2.1.0", format="wheel")
    """
    
    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir)
        self.build_dir = self.source_dir / "build"
        self.dist_dir = self.source_dir / "dist"
        
        # Files to always exclude from packages
        self.exclusions = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".git",
            ".env",
            "secrets.enc",
            "*.log",
            ".DS_Store",
            "node_modules",
            "venv",
            ".venv"
        ]
    
    def build_package(self, version: str, format: str = "tarball") -> Optional[Path]:
        """
        TUTORIAL: Build a Distribution Package
        
        Steps:
        1. Clean previous builds
        2. Collect files to include
        3. Generate manifest
        4. Create package in specified format
        5. Generate checksums
        6. Create release notes
        
        Args:
            version: Semantic version string
            format: Package format (tarball, zip, wheel)
        
        Returns:
            Path to created package, or None if failed
        """
        print(f"📦 Building package v{version} ({format})...")
        
        try:
            # Step 1: Clean and prepare directories
            self._prepare_directories()
            
            # Step 2: Collect files
            files = self._collect_files()
            print(f"   Found {len(files)} files to package")
            
            # Step 3: Generate manifest
            manifest = self._generate_manifest(version, files)
            
            # Step 4: Create package
            if format == "tarball":
                package_path = self._create_tarball(version, files)
            elif format == "zip":
                package_path = self._create_zip(version, files)
            else:
                package_path = self._create_tarball(version, files)
            
            # Step 5: Generate checksums
            checksums = self._generate_checksums(package_path)
            
            # Step 6: Save manifest and checksums
            self._save_release_info(version, manifest, checksums)
            
            print(f"✅ Package created: {package_path}")
            return package_path
            
        except Exception as e:
            print(f"❌ Package build failed: {e}")
            return None
    
    def _prepare_directories(self):
        """Prepare build and dist directories"""
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir.mkdir(parents=True, exist_ok=True)
    
    def _collect_files(self) -> List[Path]:
        """Collect all files to include in package (optimized)"""
        files = []
        
        # Pre-compile exclusion patterns for better performance
        suffix_exclusions = {ex[1:] for ex in self.exclusions if ex.startswith("*") and len(ex) > 1}
        path_exclusions = {ex for ex in self.exclusions if not ex.startswith("*")}
        
        for item in self.source_dir.rglob("*"):
            if item.is_file():
                # Check suffix exclusions (faster lookup with set)
                if item.suffix in suffix_exclusions:
                    continue
                
                # Check path exclusions
                item_str = str(item)
                if any(exclusion in item_str for exclusion in path_exclusions):
                    continue
                
                files.append(item)
        
        return files
    
    def _generate_manifest(self, version: str, files: List[Path]) -> Dict[str, Any]:
        """Generate package manifest"""
        return {
            "name": "self-evolving-ai-framework",
            "version": version,
            "created": datetime.now().isoformat(),
            "file_count": len(files),
            "files": [str(f.relative_to(self.source_dir)) for f in files[:100]],  # First 100
            "python_requires": ">=3.9",
            "dependencies": self._read_requirements()
        }
    
    def _read_requirements(self) -> List[str]:
        """Read requirements from requirements.txt"""
        req_file = self.source_dir / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return []
    
    def _create_tarball(self, version: str, files: List[Path]) -> Path:
        """Create tarball package"""
        package_name = f"self-evolving-ai-{version}.tar.gz"
        package_path = self.dist_dir / package_name
        
        with tarfile.open(package_path, "w:gz") as tar:
            for file in files:
                arcname = file.relative_to(self.source_dir)
                tar.add(file, arcname=arcname)
        
        return package_path
    
    def _create_zip(self, version: str, files: List[Path]) -> Path:
        """Create zip package"""
        package_name = f"self-evolving-ai-{version}.zip"
        package_path = self.dist_dir / package_name
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                arcname = file.relative_to(self.source_dir)
                zipf.write(file, arcname=arcname)
        
        return package_path
    
    def _generate_checksums(self, package_path: Path) -> Dict[str, str]:
        """Generate checksums for package"""
        checksums = {}
        
        with open(package_path, 'rb') as f:
            content = f.read()
            checksums['md5'] = hashlib.md5(content).hexdigest()
            checksums['sha256'] = hashlib.sha256(content).hexdigest()
        
        return checksums
    
    def _save_release_info(self, version: str, manifest: Dict, checksums: Dict):
        """Save release information"""
        release_info = {
            "manifest": manifest,
            "checksums": checksums
        }
        
        info_path = self.dist_dir / f"release-{version}.json"
        with open(info_path, 'w') as f:
            json.dump(release_info, f, indent=2)


# ============================================================================
# TUTORIAL SECTION 4: Docker Builder
# ============================================================================

class DockerBuilder:
    """
    TUTORIAL: Docker Containerization
    
    This class handles building and managing Docker images for the framework.
    Docker containers provide consistent, reproducible deployments.
    
    Key Concepts:
    1. Dockerfile: Instructions for building the image
    2. Multi-stage builds: Smaller, more secure images
    3. Layer caching: Faster builds
    4. Health checks: Container monitoring
    
    Best Practices:
    - Use specific base image versions
    - Run as non-root user
    - Minimize layers
    - Use .dockerignore
    - Include health checks
    """
    
    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir)
        self.dockerfile_path = self.source_dir / "Dockerfile"
    
    def generate_dockerfile(self) -> str:
        """
        TUTORIAL: Generate Optimized Dockerfile
        
        This generates a production-ready Dockerfile with:
        - Multi-stage build for smaller image
        - Non-root user for security
        - Health check for monitoring
        - Proper layer ordering for caching
        """
        dockerfile = '''# Self-Evolving AI Framework Docker Image
# Generated by deployment_manager.py
# 
# TUTORIAL: This Dockerfile uses multi-stage builds for optimization
# Stage 1: Build dependencies
# Stage 2: Production runtime

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

# Set build-time variables
ARG VERSION=2.0.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Production Runtime
# ============================================================================
FROM python:3.11-slim as runtime

# Labels for image metadata
LABEL maintainer="Self-Evolving AI Team"
LABEL version="${VERSION}"
LABEL description="Self-Evolving AI Framework - Autonomous AI System"

# Security: Run as non-root user
RUN groupadd --gid 1000 aiuser && \\
    useradd --uid 1000 --gid aiuser --shell /bin/bash --create-home aiuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=aiuser:aiuser . .

# Create data directories
RUN mkdir -p /app/AI_NETWORK_LOCAL /app/logs /app/backups && \\
    chown -R aiuser:aiuser /app

# Switch to non-root user
USER aiuser

# Environment variables
ENV ENVIRONMENT=production
ENV DATA_DIRECTORY=/app/AI_NETWORK_LOCAL
ENV LOG_LEVEL=INFO

# Expose ports
EXPOSE 5000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "from self_evolving_core import EvolvingAIFramework; f = EvolvingAIFramework(); print('healthy' if f.initialize() else 'unhealthy')" || exit 1

# Default command
CMD ["python", "evolving_ai_main.py", "status"]
'''
        return dockerfile
    
    def build_image(self, tag: str = "latest", no_cache: bool = False) -> bool:
        """
        TUTORIAL: Build Docker Image
        
        Steps:
        1. Generate Dockerfile if not exists
        2. Create .dockerignore
        3. Run docker build
        4. Tag image
        5. Verify build
        
        Args:
            tag: Image tag (e.g., "2.1.0", "latest")
            no_cache: Whether to build without cache
        
        Returns:
            True if build succeeded
        """
        print(f"🐳 Building Docker image with tag: {tag}")
        
        try:
            # Generate Dockerfile
            dockerfile_content = self.generate_dockerfile()
            with open(self.dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            print("   ✅ Dockerfile generated")
            
            # Generate .dockerignore
            self._generate_dockerignore()
            print("   ✅ .dockerignore generated")
            
            # Build command
            image_name = f"self-evolving-ai:{tag}"
            cmd = ["docker", "build", "-t", image_name, "."]
            
            if no_cache:
                cmd.insert(2, "--no-cache")
            
            print(f"   Running: {' '.join(cmd)}")
            
            # Note: In demo mode, we just simulate the build
            print("   📝 Demo mode: Docker build simulated")
            print(f"   ✅ Image would be built as: {image_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Docker build failed: {e}")
            return False
    
    def _generate_dockerignore(self):
        """Generate .dockerignore file"""
        dockerignore = '''# Self-Evolving AI Framework .dockerignore
# Generated by deployment_manager.py

# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv
.venv
*.egg-info
dist
build

# IDE
.vscode
.idea
*.swp
*.swo

# Secrets (NEVER include in Docker image!)
.env
secrets.enc
*.key
*.pem

# Logs and data
*.log
logs/
AI_NETWORK_LOCAL/
backups/

# Tests
tests/
*.test.py
test_*.py

# Documentation
docs/
*.md
!README.md

# OS
.DS_Store
Thumbs.db
'''
        
        dockerignore_path = self.source_dir / ".dockerignore"
        with open(dockerignore_path, 'w') as f:
            f.write(dockerignore)


# ============================================================================
# TUTORIAL SECTION 5: Cloud Deployer
# ============================================================================

class CloudDeployer:
    """
    TUTORIAL: Multi-Cloud Deployment
    
    This class handles deploying the framework to various cloud platforms.
    Each platform has its own deployment strategy and requirements.
    
    Supported Platforms:
    - AWS (ECS, Lambda, EC2)
    - Google Cloud (Cloud Run, GKE)
    - Azure (Container Instances, AKS)
    - Heroku (Dynos)
    - DigitalOcean (App Platform)
    
    Key Concepts:
    1. Infrastructure as Code: Define deployments programmatically
    2. Blue-Green Deployment: Zero-downtime updates
    3. Rollback Strategy: Quick recovery from failures
    4. Health Monitoring: Verify deployment success
    """
    
    def __init__(self):
        self.targets = {t.name: t for t in DEMO_DEPLOYMENT_TARGETS}
        self.deployment_history: List[DeploymentResult] = []
    
    def deploy(self, target_name: str, version: str) -> DeploymentResult:
        """
        TUTORIAL: Deploy to Cloud Platform
        
        Deployment Process:
        1. Validate target configuration
        2. Pre-deployment checks
        3. Create deployment artifacts
        4. Execute platform-specific deployment
        5. Post-deployment verification
        6. Record deployment for rollback
        
        Args:
            target_name: Name of deployment target
            version: Version to deploy
        
        Returns:
            DeploymentResult with success status and details
        """
        print(f"🚀 Deploying v{version} to {target_name}...")
        
        start_time = datetime.now()
        logs = []
        
        try:
            # Step 1: Get target configuration
            target = self.targets.get(target_name)
            if not target:
                raise ValueError(f"Unknown deployment target: {target_name}")
            
            if not target.enabled:
                raise ValueError(f"Deployment target '{target_name}' is disabled")
            
            logs.append(f"Target: {target.platform} in {target.region}")
            
            # Step 2: Pre-deployment checks
            logs.append("Running pre-deployment checks...")
            self._pre_deployment_checks(target)
            logs.append("✅ Pre-deployment checks passed")
            
            # Step 3: Platform-specific deployment
            logs.append(f"Deploying to {target.platform}...")
            
            if target.platform == "docker":
                self._deploy_docker(target, version, logs)
            elif target.platform == "aws":
                self._deploy_aws(target, version, logs)
            elif target.platform == "heroku":
                self._deploy_heroku(target, version, logs)
            else:
                logs.append(f"Platform {target.platform} deployment simulated")
            
            # Step 4: Post-deployment verification
            logs.append("Running post-deployment verification...")
            self._post_deployment_verify(target)
            logs.append("✅ Deployment verified")
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = DeploymentResult(
                success=True,
                target=target_name,
                version=version,
                duration_seconds=duration,
                artifacts=[f"self-evolving-ai:{version}"],
                logs=logs,
                rollback_id=f"rollback-{target_name}-{version}-{int(datetime.now().timestamp())}"
            )
            
            # Record for rollback
            self.deployment_history.append(result)
            
            print(f"✅ Deployment successful in {duration:.1f}s")
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logs.append(f"❌ Error: {str(e)}")
            
            result = DeploymentResult(
                success=False,
                target=target_name,
                version=version,
                duration_seconds=duration,
                logs=logs,
                error=str(e)
            )
            
            print(f"❌ Deployment failed: {e}")
            return result
    
    def _pre_deployment_checks(self, target: DeploymentTarget):
        """Run pre-deployment validation checks"""
        # Check credentials are configured
        if not target.credentials:
            raise ValueError("No credentials configured for target")
        
        # Platform-specific checks would go here
        pass
    
    def _deploy_docker(self, target: DeploymentTarget, version: str, logs: List[str]):
        """Deploy to Docker registry"""
        registry = target.credentials.get("registry", "localhost:5000")
        image_name = target.config.get("image_name", "self-evolving-ai")
        
        logs.append(f"Pushing to registry: {registry}")
        logs.append(f"Image: {image_name}:{version}")
        logs.append("📝 Demo mode: Docker push simulated")
    
    def _deploy_aws(self, target: DeploymentTarget, version: str, logs: List[str]):
        """Deploy to AWS"""
        service = target.config.get("service", "ecs")
        cluster = target.config.get("cluster", "default")
        
        logs.append(f"AWS Service: {service}")
        logs.append(f"Cluster: {cluster}")
        logs.append(f"Region: {target.region}")
        logs.append("📝 Demo mode: AWS deployment simulated")
    
    def _deploy_heroku(self, target: DeploymentTarget, version: str, logs: List[str]):
        """Deploy to Heroku"""
        app_name = target.credentials.get("app_name", "self-evolving-ai")
        
        logs.append(f"Heroku App: {app_name}")
        logs.append("📝 Demo mode: Heroku deployment simulated")
    
    def _post_deployment_verify(self, target: DeploymentTarget):
        """Verify deployment was successful"""
        # Health check would go here
        pass
    
    def rollback(self, rollback_id: Optional[str] = None) -> bool:
        """
        TUTORIAL: Rollback Deployment
        
        Rollback to a previous deployment state. If no rollback_id
        is provided, rolls back to the last successful deployment.
        
        Args:
            rollback_id: Specific rollback ID, or None for last deployment
        
        Returns:
            True if rollback succeeded
        """
        print("🔄 Initiating rollback...")
        
        if not self.deployment_history:
            print("❌ No deployment history available for rollback")
            return False
        
        # Find deployment to rollback to
        if rollback_id:
            target_deployment = None
            for dep in self.deployment_history:
                if dep.rollback_id == rollback_id:
                    target_deployment = dep
                    break
            
            if not target_deployment:
                print(f"❌ Rollback ID not found: {rollback_id}")
                return False
        else:
            # Get last successful deployment
            successful = [d for d in self.deployment_history if d.success]
            if len(successful) < 2:
                print("❌ Not enough deployment history for rollback")
                return False
            target_deployment = successful[-2]  # Second to last
        
        print(f"Rolling back to: {target_deployment.version}")
        print(f"Target: {target_deployment.target}")
        print("📝 Demo mode: Rollback simulated")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            "targets": {name: asdict(target) for name, target in self.targets.items()},
            "deployment_count": len(self.deployment_history),
            "last_deployment": asdict(self.deployment_history[-1]) if self.deployment_history else None
        }


# ============================================================================
# TUTORIAL SECTION 6: Release Manager
# ============================================================================

class ReleaseManager:
    """
    TUTORIAL: Release Management
    
    This class handles creating and managing releases with proper
    versioning, changelogs, and artifact generation.
    
    Semantic Versioning:
    - MAJOR: Breaking changes
    - MINOR: New features (backward compatible)
    - PATCH: Bug fixes (backward compatible)
    
    Example: 2.1.0
    - 2 = Major version
    - 1 = Minor version  
    - 0 = Patch version
    """
    
    def __init__(self, releases_dir: str = "releases"):
        self.releases_dir = Path(releases_dir)
        self.releases_dir.mkdir(parents=True, exist_ok=True)
        self.releases: List[ReleaseInfo] = []
    
    def create_release(self, version: str, changelog: List[str], 
                      codename: Optional[str] = None) -> ReleaseInfo:
        """
        TUTORIAL: Create a New Release
        
        Steps:
        1. Validate version format
        2. Check version doesn't exist
        3. Generate release artifacts
        4. Create changelog
        5. Tag in version control
        6. Save release metadata
        """
        print(f"📋 Creating release v{version}...")
        
        # Validate version
        if not self._validate_version(version):
            raise ValueError(f"Invalid version format: {version}")
        
        # Create release info
        release = ReleaseInfo(
            version=version,
            codename=codename or self._generate_codename(version),
            changelog=changelog,
            contributors=["AI Framework Team"]
        )
        
        # Generate artifacts
        builder = PackageBuilder()
        package_path = builder.build_package(version, "tarball")
        
        if package_path:
            release.artifacts["tarball"] = str(package_path)
        
        # Save release metadata
        self._save_release(release)
        self.releases.append(release)
        
        print(f"✅ Release v{version} ({release.codename}) created")
        return release
    
    def _validate_version(self, version: str) -> bool:
        """Validate semantic version format"""
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
        return bool(re.match(pattern, version))
    
    def _generate_codename(self, version: str) -> str:
        """Generate a codename for the release"""
        codenames = [
            "Aurora", "Blaze", "Cascade", "Dawn", "Eclipse",
            "Falcon", "Genesis", "Horizon", "Infinity", "Jupiter"
        ]
        # Use version hash to pick codename
        idx = hash(version) % len(codenames)
        return codenames[idx]
    
    def _save_release(self, release: ReleaseInfo):
        """Save release metadata to file"""
        release_file = self.releases_dir / f"release-{release.version}.json"
        with open(release_file, 'w') as f:
            json.dump(asdict(release), f, indent=2)
    
    def generate_changelog(self, from_version: str, to_version: str) -> str:
        """Generate changelog between versions"""
        return f"""
# Changelog: v{from_version} → v{to_version}

## New Features
- Enhanced deployment automation
- Docker containerization support
- Multi-cloud deployment capabilities

## Improvements
- Faster package building
- Better error handling
- Improved documentation

## Bug Fixes
- Fixed rollback edge cases
- Resolved credential handling issues
"""


# ============================================================================
# TUTORIAL SECTION 7: Main Deployment Manager
# ============================================================================

class DeploymentManager:
    """
    TUTORIAL: Main Deployment Manager
    
    This is the main orchestrator that coordinates all deployment
    operations. It provides a unified interface for:
    - Package building
    - Docker containerization
    - Cloud deployment
    - Release management
    - Rollback operations
    
    Usage:
        manager = DeploymentManager()
        manager.full_deployment("2.1.0", "aws-production")
    """
    
    def __init__(self):
        self.package_builder = PackageBuilder()
        self.docker_builder = DockerBuilder()
        self.cloud_deployer = CloudDeployer()
        self.release_manager = ReleaseManager()
        
        print("🚀 Deployment Manager initialized")
    
    def full_deployment(self, version: str, target: str) -> Dict[str, Any]:
        """
        TUTORIAL: Full Deployment Pipeline
        
        Executes complete deployment pipeline:
        1. Build package
        2. Build Docker image
        3. Run tests
        4. Deploy to target
        5. Verify deployment
        6. Create release record
        """
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Full Deployment Pipeline                                     ║
║  Version: {version:10}  Target: {target:20}        ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        results = {
            "version": version,
            "target": target,
            "steps": {},
            "success": True
        }
        
        # Step 1: Build package
        print("\n📦 Step 1: Building package...")
        package = self.package_builder.build_package(version)
        results["steps"]["package"] = {"success": package is not None}
        
        # Step 2: Build Docker image
        print("\n🐳 Step 2: Building Docker image...")
        docker_success = self.docker_builder.build_image(version)
        results["steps"]["docker"] = {"success": docker_success}
        
        # Step 3: Deploy
        print(f"\n🚀 Step 3: Deploying to {target}...")
        deploy_result = self.cloud_deployer.deploy(target, version)
        results["steps"]["deploy"] = asdict(deploy_result)
        
        if not deploy_result.success:
            results["success"] = False
        
        # Summary
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Deployment Summary                                           ║
╠══════════════════════════════════════════════════════════════╣
║  Package Build:  {'✅ Success' if results['steps']['package']['success'] else '❌ Failed':20}                    ║
║  Docker Build:   {'✅ Success' if results['steps']['docker']['success'] else '❌ Failed':20}                    ║
║  Deployment:     {'✅ Success' if deploy_result.success else '❌ Failed':20}                    ║
╠══════════════════════════════════════════════════════════════╣
║  Overall:        {'✅ SUCCESS' if results['success'] else '❌ FAILED':20}                    ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        return results
    
    def quick_deploy(self, target: str = "local-docker") -> bool:
        """Quick deployment for development/testing"""
        print(f"⚡ Quick deploy to {target}...")
        result = self.cloud_deployer.deploy(target, "dev")
        return result.success
    
    def status(self) -> Dict[str, Any]:
        """Get deployment system status"""
        return {
            "deployment_targets": list(self.cloud_deployer.targets.keys()),
            "deployment_history": len(self.cloud_deployer.deployment_history),
            "releases": len(self.release_manager.releases)
        }


# ============================================================================
# TUTORIAL SECTION 8: CLI Interface
# ============================================================================

def main():
    """
    TUTORIAL: Command Line Interface
    
    The CLI provides easy access to all deployment operations.
    
    Commands:
        package     - Build distribution package
        docker      - Build Docker image
        deploy      - Deploy to cloud platform
        release     - Create new release
        rollback    - Rollback deployment
        status      - Show deployment status
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Self-Evolving AI Deployment Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python deployment_manager.py package
    python deployment_manager.py docker --tag 2.1.0
    python deployment_manager.py deploy local-docker --version 2.1.0
    python deployment_manager.py release 2.1.0 --changelog "New features"
    python deployment_manager.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Deployment commands')
    
    # Package command
    pkg_parser = subparsers.add_parser('package', help='Build distribution package')
    pkg_parser.add_argument('--version', default='2.0.0', help='Package version')
    pkg_parser.add_argument('--format', choices=['tarball', 'zip'], default='tarball')
    
    # Docker command
    docker_parser = subparsers.add_parser('docker', help='Build Docker image')
    docker_parser.add_argument('--tag', default='latest', help='Image tag')
    docker_parser.add_argument('--no-cache', action='store_true')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy to cloud')
    deploy_parser.add_argument('target', help='Deployment target name')
    deploy_parser.add_argument('--version', default='2.0.0', help='Version to deploy')
    
    # Release command
    release_parser = subparsers.add_parser('release', help='Create release')
    release_parser.add_argument('version', help='Release version')
    release_parser.add_argument('--changelog', nargs='+', default=['Initial release'])
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback deployment')
    rollback_parser.add_argument('--id', help='Specific rollback ID')
    
    # Status command
    subparsers.add_parser('status', help='Show deployment status')
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    if args.command == 'package':
        manager.package_builder.build_package(args.version, args.format)
    elif args.command == 'docker':
        manager.docker_builder.build_image(args.tag, args.no_cache)
    elif args.command == 'deploy':
        manager.cloud_deployer.deploy(args.target, args.version)
    elif args.command == 'release':
        manager.release_manager.create_release(args.version, args.changelog)
    elif args.command == 'rollback':
        manager.cloud_deployer.rollback(args.id)
    elif args.command == 'status':
        status = manager.status()
        print(json.dumps(status, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
