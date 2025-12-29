#!/usr/bin/env python3
"""
Quick Deploy Script for App Productizer
Simplified deployment that handles AWS setup automatically
"""

import subprocess
import sys
import os
import json
import time

def main():
    """Quick deployment with automatic AWS setup"""
    
    print("🚀 App Productizer - Quick Deploy")
    print("=" * 50)
    
    # Step 1: Install dependencies
    print("\n📦 Installing dependencies...")
    install_dependencies()
    
    # Step 2: Install CDK CLI
    print("\n🔧 Installing AWS CDK CLI...")
    install_cdk_cli()
    
    # Step 3: Check/Setup AWS credentials
    print("\n🔐 Setting up AWS credentials...")
    setup_aws_credentials()
    
    # Step 4: Bootstrap CDK
    print("\n⚡ Bootstrapping AWS CDK...")
    bootstrap_cdk()
    
    # Step 5: Deploy infrastructure
    print("\n🏗️ Deploying infrastructure...")
    deploy_infrastructure()
    
    # Step 6: Show results
    print("\n✅ Deployment completed!")
    show_results()

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def install_cdk_cli():
    """Install AWS CDK CLI"""
    try:
        # Check if CDK is already installed
        result = subprocess.run(['cdk', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS CDK CLI already installed")
            return
    except FileNotFoundError:
        pass
    
    try:
        print("Installing AWS CDK CLI via npm...")
        # Try npm first
        subprocess.run(['npm', 'install', '-g', 'aws-cdk'], check=True)
        print("✅ AWS CDK CLI installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            print("npm not found, trying alternative installation...")
            # Alternative: install via pip
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'aws-cdk-lib[cli]'], check=True)
            print("✅ AWS CDK CLI installed via pip")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install CDK CLI: {e}")
            print("Please install Node.js or run: pip install aws-cdk-lib[cli]")
            sys.exit(1)

def setup_aws_credentials():
    """Setup AWS credentials"""
    
    # Check if credentials already exist
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS credentials already configured")
            return
    except FileNotFoundError:
        pass
    
    print("\n🔐 AWS Credentials Setup")
    print("You need AWS credentials to deploy. Choose an option:")
    print("1. I have AWS Access Key ID and Secret Access Key")
    print("2. I want to use AWS SSO/CLI login")
    print("3. I need to create an AWS account first")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        setup_access_keys()
    elif choice == "2":
        setup_sso_login()
    elif choice == "3":
        show_aws_account_setup()
    else:
        print("Invalid choice. Please run the script again.")
        sys.exit(1)

def setup_access_keys():
    """Setup AWS access keys"""
    print("\n📝 Enter your AWS credentials:")
    print("(You can find these in AWS Console > IAM > Users > Security credentials)")
    
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    region = input("Default region (press Enter for us-east-1): ").strip() or "us-east-1"
    
    if not access_key or not secret_key:
        print("❌ Access Key ID and Secret Access Key are required")
        sys.exit(1)
    
    try:
        # Configure AWS CLI
        subprocess.run(['aws', 'configure', 'set', 'aws_access_key_id', access_key], check=True)
        subprocess.run(['aws', 'configure', 'set', 'aws_secret_access_key', secret_key], check=True)
        subprocess.run(['aws', 'configure', 'set', 'default.region', region], check=True)
        subprocess.run(['aws', 'configure', 'set', 'default.output', 'json'], check=True)
        
        # Test credentials
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS credentials configured successfully")
        else:
            print("❌ Failed to configure credentials. Please check your keys.")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to configure AWS: {e}")
        sys.exit(1)

def setup_sso_login():
    """Setup AWS SSO login"""
    print("\n🔐 AWS SSO Login")
    print("This will open your browser for AWS SSO login...")
    
    try:
        subprocess.run(['aws', 'sso', 'login'], check=True)
        print("✅ AWS SSO login completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ AWS SSO login failed: {e}")
        sys.exit(1)

def show_aws_account_setup():
    """Show AWS account setup instructions"""
    print("\n🆕 AWS Account Setup")
    print("=" * 30)
    print("1. Go to https://aws.amazon.com/")
    print("2. Click 'Create an AWS Account'")
    print("3. Follow the signup process")
    print("4. Once created, go to IAM console")
    print("5. Create a new user with programmatic access")
    print("6. Attach 'AdministratorAccess' policy (for development)")
    print("7. Save the Access Key ID and Secret Access Key")
    print("8. Run this script again with option 1")
    print("\n💡 Tip: AWS Free Tier includes most services we'll use!")
    sys.exit(0)

def bootstrap_cdk():
    """Bootstrap AWS CDK"""
    try:
        print("Bootstrapping CDK (this may take a few minutes)...")
        result = subprocess.run(['cdk', 'bootstrap'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ CDK bootstrapped successfully")
        else:
            print("⚠️ CDK bootstrap completed with warnings")
            print(result.stdout)
            
    except subprocess.TimeoutExpired:
        print("⚠️ CDK bootstrap is taking longer than expected, but continuing...")
    except subprocess.CalledProcessError as e:
        print(f"❌ CDK bootstrap failed: {e}")
        print("This might be okay if CDK was already bootstrapped")

def deploy_infrastructure():
    """Deploy the CDK infrastructure"""
    try:
        print("Synthesizing CDK app...")
        result = subprocess.run(['cdk', 'synth'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ CDK synthesis failed: {result.stderr}")
            sys.exit(1)
        
        print("✅ CDK synthesis successful")
        
        print("Deploying infrastructure (this may take 10-15 minutes)...")
        result = subprocess.run(['cdk', 'deploy', '--require-approval', 'never'], 
                              capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            print("✅ Infrastructure deployed successfully!")
            return result.stdout
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("❌ Deployment timed out. Check AWS Console for status.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

def show_results():
    """Show deployment results and next steps"""
    print("\n🎉 App Productizer Successfully Deployed!")
    print("=" * 50)
    
    print("\n📋 What was created:")
    print("✅ S3 buckets for app storage and documentation")
    print("✅ Lambda functions for AI processing")
    print("✅ API Gateway for webhooks")
    print("✅ DynamoDB table for app tracking")
    print("✅ CodeBuild project for quality checks")
    print("✅ SNS topic for notifications")
    
    print("\n🔧 Next Steps:")
    print("1. Get your API Gateway URL from AWS Console")
    print("2. Configure your API keys:")
    print("   - Perplexity API key")
    print("   - Notion token")
    print("   - Zapier webhook URL")
    print("   - GitHub token")
    print("3. Update app.py with your GitHub repositories")
    print("4. Test with your first app!")
    
    print("\n🔗 Useful Commands:")
    print("- View outputs: cdk outputs")
    print("- Update deployment: cdk deploy")
    print("- View logs: Check CloudWatch in AWS Console")
    print("- Destroy (when done): cdk destroy")
    
    print("\n💰 Cost Estimate:")
    print("- Most services are in AWS Free Tier")
    print("- Expected cost: $5-20/month for moderate usage")
    print("- Lambda, S3, and DynamoDB are pay-per-use")
    
    print("\n🚀 Ready to transform your apps into products!")

if __name__ == '__main__':
    main()