"""
Documentation Generator Lambda
Uses Perplexity API to generate professional documentation for your apps
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
    Generate professional documentation for an app using AI
    """
    try:
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
            
        app_id = body.get('app_id')
        github_repo = body.get('github_repo')
        app_type = body.get('app_type', 'webapp')
        
        if not app_id or not github_repo:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'app_id and github_repo are required'})
            }
        
        # Get app configuration
        app_config = get_app_config(app_id)
        
        # Generate documentation using Perplexity
        documentation = generate_documentation_with_ai(github_repo, app_type, app_config)
        
        # Create professional README
        readme_content = create_professional_readme(app_id, documentation, app_config)
        
        # Upload to S3
        docs_bucket = os.environ['DOCS_BUCKET']
        upload_documentation(docs_bucket, app_id, readme_content, documentation)
        
        # Update status in DynamoDB
        update_app_status(app_id, 'documentation_generated', {
            'documentation_url': f"https://{docs_bucket}.s3.amazonaws.com/{app_id}/index.html",
            'generated_at': datetime.utcnow().isoformat()
        })
        
        # Trigger Zapier webhook for Notion update
        trigger_zapier_webhook('documentation_generated', {
            'app_id': app_id,
            'documentation_url': f"https://{docs_bucket}.s3.amazonaws.com/{app_id}/index.html"
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Documentation generated successfully',
                'app_id': app_id,
                'documentation_url': f"https://{docs_bucket}.s3.amazonaws.com/{app_id}/index.html"
            })
        }
        
    except Exception as e:
        print(f"Error generating documentation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_app_config(app_id: str) -> Dict[str, Any]:
    """Get app configuration from your predefined configs"""
    
    # This would typically come from your app configuration
    app_configs = {
        'ai_workflow_architect': {
            'name': 'AI Workflow Architect',
            'description': 'Multi-agent AI orchestration platform',
            'price_tier': 'enterprise',
            'target_audience': 'Enterprise teams, AI developers, Automation specialists',
            'key_features': [
                'Multi-provider AI orchestration',
                'Cost governance and budget tracking', 
                'Secure credential vault',
                'Decision tracing and approval workflows',
                'Centralized memory system'
            ]
        },
        'gumroad_automation': {
            'name': 'Gumroad Automation Toolkit',
            'description': 'AI-powered e-commerce automation for Gumroad',
            'price_tier': 'business',
            'target_audience': 'E-commerce entrepreneurs, Digital product sellers, Automation enthusiasts',
            'key_features': [
                'Automated product creation and publishing',
                'Form filling and validation',
                'Sales webhook integration',
                'Email notification systems',
                'Customer onboarding automation'
            ]
        },
        'chat_archive': {
            'name': 'Chat Archive System',
            'description': 'Professional chat management and archival tool',
            'price_tier': 'utility',
            'target_audience': 'Teams, Customer support, Content creators',
            'key_features': [
                'Automated chat archiving',
                'Search and retrieval',
                'Export capabilities',
                'Integration with popular chat platforms'
            ]
        }
    }
    
    return app_configs.get(app_id, {})

def generate_documentation_with_ai(github_repo: str, app_type: str, app_config: Dict[str, Any]) -> Dict[str, Any]:
    """Use Perplexity API to generate comprehensive documentation"""
    
    perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
    if not perplexity_api_key:
        return generate_fallback_documentation(app_config)
    
    try:
        # Construct prompt for Perplexity
        prompt = f"""
        Create comprehensive, professional documentation for a {app_type} application with these details:
        
        App Name: {app_config.get('name', 'Application')}
        Description: {app_config.get('description', 'A professional application')}
        Target Audience: {app_config.get('target_audience', 'Professional users')}
        Key Features: {', '.join(app_config.get('key_features', []))}
        
        Please generate:
        1. Professional product description (2-3 paragraphs)
        2. Feature list with benefits
        3. Installation instructions
        4. Usage examples
        5. API documentation (if applicable)
        6. Troubleshooting guide
        7. Support information
        
        Make it sound professional and sellable, suitable for a Gumroad product listing.
        """
        
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {perplexity_api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.1-sonar-small-128k-online',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional technical writer creating documentation for software products.'
                    },
                    {
                        'role': 'user', 
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return {
                'generated_content': content,
                'source': 'perplexity_ai',
                'generated_at': datetime.utcnow().isoformat()
            }
        else:
            print(f"Perplexity API error: {response.status_code} - {response.text}")
            return generate_fallback_documentation(app_config)
            
    except Exception as e:
        print(f"Error calling Perplexity API: {str(e)}")
        return generate_fallback_documentation(app_config)

def generate_fallback_documentation(app_config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic documentation when AI is not available"""
    
    name = app_config.get('name', 'Application')
    description = app_config.get('description', 'A professional application')
    features = app_config.get('key_features', [])
    
    content = f"""# {name}

## Overview

{description}

## Key Features

{chr(10).join(f"- {feature}" for feature in features)}

## Installation

1. Download the application files
2. Follow the setup instructions in the included guide
3. Configure your environment variables
4. Run the application

## Usage

Detailed usage instructions are provided in the application interface.

## Support

For support and questions, please refer to the documentation or contact support.

## License

Professional license included with purchase.
"""
    
    return {
        'generated_content': content,
        'source': 'fallback',
        'generated_at': datetime.utcnow().isoformat()
    }

def create_professional_readme(app_id: str, documentation: Dict[str, Any], app_config: Dict[str, Any]) -> str:
    """Create a professional README with proper formatting"""
    
    name = app_config.get('name', 'Application')
    price_tier = app_config.get('price_tier', 'standard')
    
    # Price mapping
    price_map = {
        'utility': '$29-49',
        'business': '$49-99', 
        'enterprise': '$99-299'
    }
    
    price_range = price_map.get(price_tier, '$49-99')
    
    readme = f"""# {name}

> Professional {app_config.get('description', 'application')} - Ready for commercial use

[![License](https://img.shields.io/badge/license-Commercial-blue.svg)](LICENSE)
[![Price Range](https://img.shields.io/badge/price-{price_range.replace('$', '%24')}-green.svg)](https://gumroad.com)
[![Support](https://img.shields.io/badge/support-included-brightgreen.svg)](mailto:support@example.com)

## 🚀 What You Get

This is a **production-ready, professionally packaged** application that you can use immediately in your business or projects.

{documentation.get('generated_content', 'Professional application ready for deployment.')}

## 📦 Package Contents

- ✅ Complete source code
- ✅ Professional documentation
- ✅ Setup and deployment guides
- ✅ Configuration examples
- ✅ Support and updates
- ✅ Commercial license

## 🛠 Quick Start

1. **Download** your purchase from Gumroad
2. **Extract** the files to your desired location
3. **Follow** the setup guide (included)
4. **Deploy** and start using immediately

## 💼 Commercial Use

This application is licensed for commercial use. You can:
- Use in your business projects
- Modify and customize as needed
- Deploy to your own infrastructure
- Integrate with your existing systems

## 🔧 Technical Requirements

- Modern web browser or appropriate runtime environment
- Basic technical knowledge for setup
- Internet connection for initial configuration

## 📞 Support

- **Email Support**: Included with purchase
- **Documentation**: Comprehensive guides included
- **Updates**: Free updates for 1 year
- **Community**: Access to user community

## 🏷 License

Commercial license included. See LICENSE file for full terms.

---

**Ready to get started?** [Purchase on Gumroad](https://gumroad.com) and start using this professional application today!

*Generated on {datetime.utcnow().strftime('%Y-%m-%d')} - Version 1.0*
"""
    
    return readme

def upload_documentation(bucket: str, app_id: str, readme_content: str, documentation: Dict[str, Any]) -> None:
    """Upload documentation to S3"""
    
    # Upload README as index.html (converted to HTML)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Documentation - {app_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
        h1, h2, h3 {{ color: #333; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 3px; 
                 background: #007cba; color: white; font-size: 12px; margin: 2px; }}
    </style>
</head>
<body>
    <div id="content"></div>
    <script>
        // Simple markdown to HTML converter
        const markdown = `{readme_content.replace('`', '\\`')}`;
        const html = markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/!\[([^\]]*)\]\(([^\)]*)\)/gim, '<img alt="$1" src="$2" />')
            .replace(/\[([^\]]*)\]\(([^\)]*)\)/gim, '<a href="$2">$1</a>')
            .replace(/\n/gim, '<br>');
        document.getElementById('content').innerHTML = html;
    </script>
</body>
</html>"""
    
    s3.put_object(
        Bucket=bucket,
        Key=f"{app_id}/index.html",
        Body=html_content,
        ContentType='text/html',
        ACL='public-read'
    )
    
    # Upload raw README
    s3.put_object(
        Bucket=bucket,
        Key=f"{app_id}/README.md",
        Body=readme_content,
        ContentType='text/markdown',
        ACL='public-read'
    )
    
    # Upload documentation metadata
    s3.put_object(
        Bucket=bucket,
        Key=f"{app_id}/documentation.json",
        Body=json.dumps(documentation, indent=2),
        ContentType='application/json',
        ACL='public-read'
    )

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
    """Trigger Zapier webhook for workflow automation"""
    
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