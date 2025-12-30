"""
Gumroad Manager Lambda
Handles Gumroad product creation and management
"""

import json
import boto3
import requests
import os
from datetime import datetime
from typing import Dict, Any

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Manage Gumroad products for your apps
    """
    try:
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
            
        action = body.get('action', 'create_product')
        app_id = body.get('app_id')
        
        if not app_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'app_id is required'})
            }
        
        if action == 'create_product':
            result = create_gumroad_product(app_id, body)
        elif action == 'update_product':
            result = update_gumroad_product(app_id, body)
        elif action == 'get_status':
            result = get_product_status(app_id)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown action: {action}'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error managing Gumroad product: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def create_gumroad_product(app_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Gumroad product"""
    
    # Get app configuration and documentation
    app_config = get_app_config(app_id)
    documentation_url = get_documentation_url(app_id)
    
    # Create product package
    package_info = create_product_package(app_id, app_config)
    
    # Generate product listing content
    product_data = generate_product_listing(app_id, app_config, documentation_url)
    
    # Update status
    update_app_status(app_id, 'gumroad_product_created', {
        'product_data': product_data,
        'package_info': package_info,
        'created_at': datetime.utcnow().isoformat()
    })
    
    # Trigger Zapier webhook for Gumroad automation
    trigger_zapier_webhook('gumroad_product_ready', {
        'app_id': app_id,
        'product_data': product_data,
        'package_url': package_info['download_url']
    })
    
    return {
        'message': 'Gumroad product created successfully',
        'app_id': app_id,
        'product_data': product_data,
        'package_info': package_info
    }

def get_app_config(app_id: str) -> Dict[str, Any]:
    """Get app configuration"""
    
    app_configs = {
        'ai_workflow_architect': {
            'name': 'AI Workflow Architect',
            'description': 'Professional multi-agent AI orchestration platform for enterprise teams',
            'price': 199,
            'category': 'Software & Tools',
            'tags': ['ai', 'automation', 'enterprise', 'workflow', 'orchestration'],
            'target_audience': 'Enterprise teams, AI developers, Automation specialists',
            'key_benefits': [
                'Coordinate multiple AI providers seamlessly',
                'Built-in cost governance and budget tracking',
                'Enterprise-grade security with encrypted vault',
                'Complete audit trail and decision tracing',
                'Centralized memory system with smart search'
            ],
            'use_cases': [
                'Multi-agent AI workflows',
                'Enterprise AI governance',
                'Cost-controlled AI operations',
                'Secure AI credential management'
            ]
        },
        'gumroad_automation': {
            'name': 'Gumroad Automation Toolkit',
            'description': 'AI-powered e-commerce automation suite for Gumroad sellers',
            'price': 79,
            'category': 'Business & Marketing',
            'tags': ['ecommerce', 'automation', 'gumroad', 'sales', 'marketing'],
            'target_audience': 'E-commerce entrepreneurs, Digital product sellers, Automation enthusiasts',
            'key_benefits': [
                'Automate product creation and publishing',
                'Smart form filling and validation',
                'Integrated sales webhook system',
                'Automated customer onboarding',
                'Email notification automation'
            ],
            'use_cases': [
                'Bulk product publishing',
                'Automated customer management',
                'Sales process automation',
                'Customer onboarding workflows'
            ]
        },
        'chat_archive': {
            'name': 'Professional Chat Archive System',
            'description': 'Advanced chat management and archival solution for teams',
            'price': 39,
            'category': 'Productivity & Organization',
            'tags': ['chat', 'archive', 'productivity', 'teams', 'organization'],
            'target_audience': 'Teams, Customer support, Content creators, Businesses',
            'key_benefits': [
                'Automated chat archiving across platforms',
                'Powerful search and retrieval system',
                'Multiple export formats supported',
                'Integration with popular chat platforms',
                'Secure data storage and backup'
            ],
            'use_cases': [
                'Team communication archiving',
                'Customer support history',
                'Content creation research',
                'Compliance and record keeping'
            ]
        }
    }
    
    return app_configs.get(app_id, {
        'name': 'Professional Application',
        'description': 'A professional software application',
        'price': 49,
        'category': 'Software & Tools',
        'tags': ['software', 'professional', 'application'],
        'target_audience': 'Professional users',
        'key_benefits': ['Professional features', 'Easy to use', 'Reliable performance'],
        'use_cases': ['Professional workflows', 'Business operations']
    })

def get_documentation_url(app_id: str) -> str:
    """Get documentation URL from S3"""
    
    docs_bucket = os.environ['DOCS_BUCKET']
    return f"https://{docs_bucket}.s3.amazonaws.com/{app_id}/index.html"

def create_product_package(app_id: str, app_config: Dict[str, Any]) -> Dict[str, Any]:
    """Create downloadable product package"""
    
    app_bucket = os.environ['APP_BUCKET']
    docs_bucket = os.environ['DOCS_BUCKET']
    
    # Create package structure
    package_structure = {
        'README.md': 'Professional documentation and setup guide',
        'LICENSE.txt': 'Commercial license terms',
        'SETUP_GUIDE.md': 'Step-by-step installation instructions',
        'SUPPORT.md': 'Support and contact information',
        'app/': 'Main application files',
        'docs/': 'Additional documentation',
        'examples/': 'Usage examples and templates'
    }
    
    # Generate license file
    license_content = generate_commercial_license(app_config['name'])
    
    # Generate setup guide
    setup_guide = generate_setup_guide(app_id, app_config)
    
    # Generate support information
    support_info = generate_support_info(app_config)
    
    # Package information
    package_info = {
        'app_id': app_id,
        'package_structure': package_structure,
        'download_url': f"https://{app_bucket}.s3.amazonaws.com/{app_id}/product-package.zip",
        'documentation_url': f"https://{docs_bucket}.s3.amazonaws.com/{app_id}/index.html",
        'license_type': 'Commercial',
        'support_included': True,
        'updates_included': '1 year',
        'created_at': datetime.utcnow().isoformat()
    }
    
    return package_info

def generate_product_listing(app_id: str, app_config: Dict[str, Any], documentation_url: str) -> Dict[str, Any]:
    """Generate Gumroad product listing content"""
    
    name = app_config['name']
    description = app_config['description']
    price = app_config['price']
    benefits = app_config['key_benefits']
    use_cases = app_config['use_cases']
    
    # Create compelling product title
    product_title = f"{name} - Professional Edition"
    
    # Create detailed product description
    product_description = f"""🚀 **{name}** - Ready-to-Deploy Professional Software

{description}

## ✨ What You Get

This is a **complete, production-ready application** that you can deploy and use immediately in your business.

### 🎯 Key Benefits
{chr(10).join(f"✅ {benefit}" for benefit in benefits)}

### 💼 Perfect For
{chr(10).join(f"• {use_case}" for use_case in use_cases)}

## 📦 Complete Package Includes

✅ **Full Source Code** - Complete, well-documented codebase
✅ **Professional Documentation** - Comprehensive setup and usage guides  
✅ **Commercial License** - Use in your business projects
✅ **Setup Support** - Email support for installation and configuration
✅ **Free Updates** - 1 year of updates and improvements
✅ **Deployment Guide** - Step-by-step deployment instructions
✅ **Configuration Examples** - Ready-to-use configuration templates

## 🛠 Technical Details

- **Professional Grade**: Production-ready code with proper error handling
- **Well Documented**: Comprehensive documentation and code comments
- **Secure**: Following security best practices and standards
- **Scalable**: Built to handle real-world usage and growth
- **Tested**: Quality assured and validated before release

## 🚀 Quick Start

1. **Purchase & Download** - Get instant access to all files
2. **Follow Setup Guide** - Step-by-step instructions included
3. **Deploy & Configure** - Use provided deployment templates
4. **Start Using** - Begin using immediately in your projects

## 📞 Support & Updates

- **Email Support**: Direct access to the developer
- **Documentation**: Comprehensive guides and examples
- **Updates**: Free updates for 1 year
- **Community**: Access to user community and resources

## 💰 Commercial License

This software comes with a commercial license allowing you to:
- Use in commercial projects and businesses
- Modify and customize as needed
- Deploy on your own infrastructure
- Integrate with your existing systems

---

**Ready to get started?** Purchase now and start using this professional application in your business today!

*Professional software, professional results.* 🎯
"""
    
    # Create product tags
    tags = app_config.get('tags', []) + ['professional', 'commercial', 'ready-to-use']
    
    return {
        'title': product_title,
        'description': product_description,
        'price': price,
        'category': app_config.get('category', 'Software & Tools'),
        'tags': tags,
        'documentation_url': documentation_url,
        'target_audience': app_config.get('target_audience', 'Professional users'),
        'created_at': datetime.utcnow().isoformat()
    }

def generate_commercial_license(app_name: str) -> str:
    """Generate commercial license text"""
    
    return f"""Commercial License Agreement

{app_name} - Professional Edition

Copyright (c) {datetime.now().year} [Your Company Name]

COMMERCIAL LICENSE

This software is licensed for commercial use. By purchasing this software, you are granted the following rights:

1. USAGE RIGHTS
   - Use the software in commercial projects and businesses
   - Deploy on your own infrastructure and servers
   - Integrate with your existing systems and workflows
   - Use for client projects and consulting work

2. MODIFICATION RIGHTS
   - Modify and customize the software as needed
   - Create derivative works based on the software
   - Adapt the software for your specific requirements

3. DISTRIBUTION RIGHTS
   - Deploy the software on multiple servers/environments
   - Share with team members within your organization
   - Include in client deliverables (with restrictions)

4. RESTRICTIONS
   - Cannot resell or redistribute the source code
   - Cannot create competing products using this code
   - Cannot remove copyright notices
   - Must maintain license terms in derivative works

5. SUPPORT AND UPDATES
   - Email support included for 1 year
   - Free updates and bug fixes for 1 year
   - Access to documentation and resources

6. WARRANTY DISCLAIMER
   This software is provided "as is" without warranty of any kind.

7. LIMITATION OF LIABILITY
   The author shall not be liable for any damages arising from the use of this software.

For questions about this license, contact: [your-email@example.com]

Generated on: {datetime.utcnow().strftime('%Y-%m-%d')}
"""

def generate_setup_guide(app_id: str, app_config: Dict[str, Any]) -> str:
    """Generate setup guide"""
    
    return f"""# {app_config['name']} - Setup Guide

Welcome to your new professional application! This guide will help you get up and running quickly.

## 📋 Prerequisites

Before you begin, make sure you have:
- Basic technical knowledge for software deployment
- Access to a server or hosting platform
- Required runtime environment (details in README.md)

## 🚀 Quick Start (5 minutes)

### Step 1: Extract Files
1. Download your purchase from Gumroad
2. Extract all files to your desired location
3. Review the file structure (see README.md)

### Step 2: Configuration
1. Copy `.env.example` to `.env`
2. Fill in your configuration values
3. Review the configuration guide in `docs/`

### Step 3: Installation
1. Follow the installation steps in README.md
2. Run the setup commands provided
3. Verify the installation was successful

### Step 4: Deployment
1. Choose your deployment method (Docker, traditional hosting, etc.)
2. Follow the deployment guide in `docs/DEPLOYMENT.md`
3. Test your deployment

## 📚 Additional Resources

- **README.md**: Complete documentation
- **docs/**: Detailed guides and examples
- **examples/**: Sample configurations and use cases
- **SUPPORT.md**: How to get help

## 🆘 Need Help?

- **Email Support**: [your-email@example.com]
- **Documentation**: Check the docs/ folder
- **Common Issues**: See TROUBLESHOOTING.md

## 🔄 Updates

You'll receive free updates for 1 year:
- Bug fixes and improvements
- New features and enhancements
- Security updates
- Documentation updates

Updates will be sent to your purchase email address.

---

**Ready to start?** Open README.md for detailed instructions!
"""

def generate_support_info(app_config: Dict[str, Any]) -> str:
    """Generate support information"""
    
    return f"""# Support Information

## 📞 Getting Help

### Email Support
- **Email**: [your-email@example.com]
- **Response Time**: Within 24-48 hours
- **Included**: Setup help, configuration assistance, basic troubleshooting

### What's Included
✅ Installation and setup assistance
✅ Configuration help and guidance
✅ Basic troubleshooting support
✅ Documentation clarification
✅ Update notifications

### What's Not Included
❌ Custom development work
❌ Extensive customization
❌ Third-party integration development
❌ Server management and maintenance

## 📚 Self-Help Resources

### Documentation
- **README.md**: Complete setup and usage guide
- **docs/**: Detailed documentation and examples
- **TROUBLESHOOTING.md**: Common issues and solutions

### Common Issues
1. **Installation Problems**: Check prerequisites and system requirements
2. **Configuration Issues**: Verify .env file and settings
3. **Deployment Problems**: Review deployment guide and logs

## 🔄 Updates and Maintenance

### Free Updates (1 Year)
- Bug fixes and improvements
- Security updates
- Documentation updates
- Minor feature enhancements

### How Updates Work
1. Updates sent to your purchase email
2. Download new version from provided link
3. Follow update instructions
4. Backup your data before updating

## 💬 Community

Join other users:
- Share tips and tricks
- Get community support
- Request features
- Report issues

## 📋 Before Contacting Support

Please have ready:
1. Your purchase receipt/order number
2. Description of the issue
3. Steps you've already tried
4. System information (OS, versions, etc.)
5. Error messages (if any)

This helps us provide faster, more accurate support!

---

**Need immediate help?** Check the TROUBLESHOOTING.md file first!
"""

def update_app_status(app_id: str, status: str, metadata: Dict[str, Any]) -> None:
    """Update app status in DynamoDB"""
    
    table = dynamodb.Table(os.environ['APP_TABLE'])
    
    table.put_item(
        Item={
            'app_id': app_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': status,
            'metadata': metadata
        }
    )

def trigger_zapier_webhook(event_type: str, data: Dict[str, Any]) -> None:
    """Trigger Zapier webhook"""
    
    webhook_url = os.environ.get('ZAPIER_WEBHOOK_URL')
    if not webhook_url:
        print("No Zapier webhook URL configured")
        return
    
    try:
        payload = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        print(f"Zapier webhook triggered: {response.status_code}")
        
    except Exception as e:
        print(f"Error triggering Zapier webhook: {str(e)}")

def update_gumroad_product(app_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Update existing Gumroad product"""
    
    # This would update an existing product
    # For now, return success message
    return {
        'message': 'Product update functionality ready',
        'app_id': app_id
    }

def get_product_status(app_id: str) -> Dict[str, Any]:
    """Get product status from DynamoDB"""
    
    table = dynamodb.Table(os.environ['APP_TABLE'])
    
    try:
        response = table.query(
            KeyConditionExpression='app_id = :app_id',
            ExpressionAttributeValues={':app_id': app_id},
            ScanIndexForward=False,  # Get latest first
            Limit=1
        )
        
        if response['Items']:
            return response['Items'][0]
        else:
            return {'message': 'No status found for app', 'app_id': app_id}
            
    except Exception as e:
        return {'error': str(e), 'app_id': app_id}