#!/usr/bin/env python3
"""
Self-Evolving AI Framework - Commercial Deployment Script
========================================================

Production deployment automation for AWS, Docker, and Kubernetes.
Supports multiple environments and deployment strategies.

Usage:
    python deploy.py --environment production --region us-east-1
    python deploy.py --docker --tag v3.0.0
    python deploy.py --kubernetes --namespace evolving-ai
"""

import argparse
import json
import os
import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """Manages deployment across different platforms"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = Path(__file__).parent
        self.version = "3.0.0"
        
    def deploy_aws(self, environment: str, region: str) -> bool:
        """Deploy to AWS using CDK"""
        logger.info(f"Deploying to AWS {environment} in {region}")
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env.update({
                'AWS_DEFAULT_REGION': region,
                'ENVIRONMENT': environment,
                'VERSION': self.version
            })
            
            # Install CDK if not present
            subprocess.run(['npm', 'install', '-g', 'aws-cdk'], check=True)
            
            # Bootstrap CDK (if needed)
            subprocess.run([
                'cdk', 'bootstrap', f'aws://unknown-account/{region}'
            ], env=env, check=False)  # Don't fail if already bootstrapped
            
            # Deploy stack
            result = subprocess.run([
                'cdk', 'deploy', '--require-approval', 'never'
            ], env=env, cwd=self.project_root, check=True)
            
            logger.info("✅ AWS deployment successful")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ AWS deployment failed: {e}")
            return False
    
    def deploy_docker(self, tag: str, push: bool = True) -> bool:
        """Build and optionally push Docker image"""
        logger.info(f"Building Docker image with tag: {tag}")
        
        try:
            # Build image
            subprocess.run([
                'docker', 'build', 
                '-t', f'evolving-ai-framework:{tag}',
                '-t', f'evolving-ai-framework:latest',
                '.'
            ], cwd=self.project_root, check=True)
            
            if push:
                # Push to registry (assumes Docker Hub or ECR)
                subprocess.run([
                    'docker', 'push', f'evolving-ai-framework:{tag}'
                ], check=True)
                subprocess.run([
                    'docker', 'push', f'evolving-ai-framework:latest'
                ], check=True)
                logger.info("✅ Docker image pushed to registry")
            
            logger.info("✅ Docker build successful")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Docker deployment failed: {e}")
            return False
    
    def deploy_kubernetes(self, namespace: str, image_tag: str) -> bool:
        """Deploy to Kubernetes cluster"""
        logger.info(f"Deploying to Kubernetes namespace: {namespace}")
        
        try:
            # Create namespace if it doesn't exist
            subprocess.run([
                'kubectl', 'create', 'namespace', namespace
            ], check=False)  # Don't fail if exists
            
            # Apply Kubernetes manifests
            k8s_dir = self.project_root / 'k8s'
            if k8s_dir.exists():
                # Update image tag in deployment
                self._update_k8s_image_tag(k8s_dir, image_tag)
                
                subprocess.run([
                    'kubectl', 'apply', '-f', str(k8s_dir), '-n', namespace
                ], check=True)
                
                # Wait for deployment to be ready
                subprocess.run([
                    'kubectl', 'rollout', 'status', 
                    'deployment/evolving-ai-framework', '-n', namespace
                ], check=True)
                
                logger.info("✅ Kubernetes deployment successful")
                return True
            else:
                logger.error("❌ Kubernetes manifests not found in k8s/")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Kubernetes deployment failed: {e}")
            return False
    
    def _update_k8s_image_tag(self, k8s_dir: Path, tag: str) -> None:
        """Update image tag in Kubernetes deployment files"""
        for yaml_file in k8s_dir.glob('*.yaml'):
            content = yaml_file.read_text()
            # Simple replacement - in production, use proper YAML parsing
            content = content.replace(
                'image: evolving-ai-framework:latest',
                f'image: evolving-ai-framework:{tag}'
            )
            yaml_file.write_text(content)
    
    def create_env_file(self, environment: str) -> bool:
        """Create environment-specific .env file"""
        logger.info(f"Creating .env file for {environment}")
        
        env_template = {
            'development': {
                'ENVIRONMENT': 'development',
                'DEBUG': 'true',
                'LOG_LEVEL': 'DEBUG',
                'OPENAI_API_KEY': 'your-openai-key',
                'ANTHROPIC_API_KEY': 'your-anthropic-key',
                'AWS_REGION': 'us-east-1',
                'STORAGE_LOCAL_PATH': './AI_NETWORK_LOCAL',
                'AUTONOMY_LEVEL': '0.5',
                'AUTO_APPROVE_THRESHOLD': '3.0'
            },
            'staging': {
                'ENVIRONMENT': 'staging',
                'DEBUG': 'false',
                'LOG_LEVEL': 'INFO',
                'OPENAI_API_KEY': '${OPENAI_API_KEY}',
                'ANTHROPIC_API_KEY': '${ANTHROPIC_API_KEY}',
                'AWS_REGION': 'us-east-1',
                'STORAGE_LOCAL_PATH': '/app/data',
                'AUTONOMY_LEVEL': '0.7',
                'AUTO_APPROVE_THRESHOLD': '2.0'
            },
            'production': {
                'ENVIRONMENT': 'production',
                'DEBUG': 'false',
                'LOG_LEVEL': 'WARNING',
                'OPENAI_API_KEY': '${OPENAI_API_KEY}',
                'ANTHROPIC_API_KEY': '${ANTHROPIC_API_KEY}',
                'AWS_REGION': 'us-east-1',
                'STORAGE_LOCAL_PATH': '/app/data',
                'AUTONOMY_LEVEL': '0.8',
                'AUTO_APPROVE_THRESHOLD': '1.5',
                'SENTRY_DSN': '${SENTRY_DSN}',
                'PROMETHEUS_PORT': '9090'
            }
        }
        
        try:
            env_vars = env_template.get(environment, env_template['development'])
            env_file = self.project_root / f'.env.{environment}'
            
            with open(env_file, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f'{key}={value}\n')
            
            logger.info(f"✅ Created {env_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create env file: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """Run post-deployment health checks"""
        logger.info("Running health checks...")
        
        try:
            # Test framework initialization
            result = subprocess.run([
                sys.executable, 'evolving_ai_main.py', 'status'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Framework health check passed")
                return True
            else:
                logger.error(f"❌ Health check failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
    
    def generate_deployment_report(self, deployment_type: str, success: bool) -> None:
        """Generate deployment report"""
        report = {
            'deployment_type': deployment_type,
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'environment': self.config.get('environment', 'unknown'),
            'region': self.config.get('region', 'unknown')
        }
        
        report_file = self.project_root / f'deployment_report_{deployment_type}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Deployment report saved to {report_file}")


def create_dockerfile() -> None:
    """Create production Dockerfile"""
    dockerfile_content = '''# Self-Evolving AI Framework - Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV STORAGE_LOCAL_PATH=/app/data
ENV ENVIRONMENT=production

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python evolving_ai_main.py status || exit 1

# Run application
CMD ["python", "evolving_ai_main.py", "start"]
'''
    
    with open('app-productizer/Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    logger.info("✅ Created production Dockerfile")


def create_k8s_manifests() -> None:
    """Create Kubernetes deployment manifests"""
    k8s_dir = Path('app-productizer/k8s')
    k8s_dir.mkdir(exist_ok=True)
    
    # Deployment manifest
    deployment_yaml = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: evolving-ai-framework
  labels:
    app: evolving-ai-framework
spec:
  replicas: 3
  selector:
    matchLabels:
      app: evolving-ai-framework
  template:
    metadata:
      labels:
        app: evolving-ai-framework
    spec:
      containers:
      - name: evolving-ai-framework
        image: evolving-ai-framework:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: anthropic-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: evolving-ai-service
spec:
  selector:
    app: evolving-ai-framework
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: ai-secrets
type: Opaque
data:
  # Base64 encoded API keys (replace with actual values)
  openai-api-key: eW91ci1vcGVuYWkta2V5
  anthropic-api-key: eW91ci1hbnRocm9waWMta2V5
'''
    
    with open(k8s_dir / 'deployment.yaml', 'w') as f:
        f.write(deployment_yaml)
    
    logger.info("✅ Created Kubernetes manifests")


def main():
    parser = argparse.ArgumentParser(
        description="Self-Evolving AI Framework Deployment Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--environment', '-e', 
                       choices=['development', 'staging', 'production'],
                       default='development',
                       help='Deployment environment')
    
    parser.add_argument('--region', '-r', default='us-east-1',
                       help='AWS region for deployment')
    
    parser.add_argument('--docker', action='store_true',
                       help='Deploy using Docker')
    
    parser.add_argument('--kubernetes', action='store_true',
                       help='Deploy to Kubernetes')
    
    parser.add_argument('--aws', action='store_true',
                       help='Deploy to AWS')
    
    parser.add_argument('--tag', '-t', default='latest',
                       help='Docker image tag')
    
    parser.add_argument('--namespace', '-n', default='default',
                       help='Kubernetes namespace')
    
    parser.add_argument('--create-manifests', action='store_true',
                       help='Create deployment manifests')
    
    parser.add_argument('--health-check', action='store_true',
                       help='Run health check only')
    
    args = parser.parse_args()
    
    # Create deployment manifests if requested
    if args.create_manifests:
        create_dockerfile()
        create_k8s_manifests()
        return
    
    # Initialize deployment manager
    config = {
        'environment': args.environment,
        'region': args.region,
        'tag': args.tag,
        'namespace': args.namespace
    }
    
    deployer = DeploymentManager(config)
    
    # Create environment file
    deployer.create_env_file(args.environment)
    
    # Run health check only
    if args.health_check:
        success = deployer.run_health_check()
        sys.exit(0 if success else 1)
    
    # Determine deployment type
    deployment_success = True
    deployment_type = "local"
    
    if args.aws:
        deployment_type = "aws"
        deployment_success = deployer.deploy_aws(args.environment, args.region)
    elif args.docker:
        deployment_type = "docker"
        deployment_success = deployer.deploy_docker(args.tag)
    elif args.kubernetes:
        deployment_type = "kubernetes"
        deployment_success = deployer.deploy_kubernetes(args.namespace, args.tag)
    
    # Run health check after deployment
    if deployment_success:
        health_success = deployer.run_health_check()
        deployment_success = deployment_success and health_success
    
    # Generate report
    deployer.generate_deployment_report(deployment_type, deployment_success)
    
    if deployment_success:
        logger.info("🎉 Deployment completed successfully!")
        print(f"\n✅ Self-Evolving AI Framework v{deployer.version} deployed")
        print(f"   Environment: {args.environment}")
        print(f"   Type: {deployment_type}")
        if args.docker:
            print(f"   Image: evolving-ai-framework:{args.tag}")
        if args.kubernetes:
            print(f"   Namespace: {args.namespace}")
    else:
        logger.error("❌ Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()