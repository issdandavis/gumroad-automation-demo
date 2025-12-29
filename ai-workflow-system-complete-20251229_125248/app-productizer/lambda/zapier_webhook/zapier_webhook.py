"""
Zapier Webhook Lambda
Handles Zapier integration for workflow automation
"""

import json
import boto3
import requests
import os
from datetime import datetime
from typing import Dict, Any

dynamodb = boto3.resource('dynamodb')

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handle Zapier webhook events
    """
    try:
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
            
        event_type = body.get('event_type')
        data = body.get('data', {})
        
        if not event_type:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'event_type is required'})
            }
        
        # Process different event types
        if event_type == 'documentation_generated':
            result = handle_documentation_generated(data)
        elif event_type == 'quality_check_completed':
            result = handle_quality_check_completed(data)
        elif event_type == 'gumroad_product_ready':
            result = handle_gumroad_product_ready(data)
        else:
            result = handle_generic_event(event_type, data)
        
        # Log the event
        log_zapier_event(event_type, data, result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Zapier webhook processed successfully',
                'event_type': event_type,
                'result': result
            })
        }
        
    except Exception as e:
        print(f"Error processing Zapier webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_documentation_generated(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle documentation generation completion"""
    
    app_id = data.get('app_id')
    documentation_url = data.get('documentation_url')
    
    # Trigger Zapier webhook to update Notion
    webhook_payload = {
        'trigger': 'documentation_ready',
        'app_name': app_id.replace('_', ' ').title(),
        'documentation_url': documentation_url,
        'status': 'Documentation Generated',
        'next_step': 'Quality Check',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    send_to_zapier(webhook_payload)
    
    return {
        'action': 'notion_updated',
        'app_id': app_id,
        'documentation_url': documentation_url
    }

def handle_quality_check_completed(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle quality check completion"""
    
    app_id = data.get('app_id')
    overall_score = data.get('overall_score', 0)
    passed = overall_score >= 80
    
    # Determine next steps based on quality score
    if passed:
        status = 'Quality Check Passed'
        next_step = 'Ready for Gumroad'
        priority = 'High'
    else:
        status = 'Quality Check Failed'
        next_step = 'Needs Improvement'
        priority = 'Medium'
    
    webhook_payload = {
        'trigger': 'quality_check_complete',
        'app_name': app_id.replace('_', ' ').title(),
        'quality_score': overall_score,
        'status': status,
        'next_step': next_step,
        'priority': priority,
        'passed': passed,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    send_to_zapier(webhook_payload)
    
    return {
        'action': 'quality_check_processed',
        'app_id': app_id,
        'passed': passed,
        'score': overall_score
    }

def handle_gumroad_product_ready(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Gumroad product ready event"""
    
    app_id = data.get('app_id')
    product_data = data.get('product_data', {})
    package_url = data.get('package_url')
    
    webhook_payload = {
        'trigger': 'product_ready_for_sale',
        'app_name': product_data.get('title', app_id.replace('_', ' ').title()),
        'price': product_data.get('price', 0),
        'description': product_data.get('description', ''),
        'package_url': package_url,
        'status': 'Ready for Gumroad',
        'next_step': 'Create Gumroad Listing',
        'priority': 'High',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    send_to_zapier(webhook_payload)
    
    return {
        'action': 'gumroad_product_ready',
        'app_id': app_id,
        'product_title': product_data.get('title')
    }

def handle_generic_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generic events"""
    
    webhook_payload = {
        'trigger': 'generic_event',
        'event_type': event_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    send_to_zapier(webhook_payload)
    
    return {
        'action': 'generic_event_processed',
        'event_type': event_type
    }

def send_to_zapier(payload: Dict[str, Any]) -> None:
    """Send payload to Zapier webhook"""
    
    webhook_url = os.environ.get('ZAPIER_WEBHOOK_URL')
    if not webhook_url:
        print("No Zapier webhook URL configured")
        return
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Successfully sent to Zapier: {payload['trigger']}")
        else:
            print(f"Zapier webhook failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error sending to Zapier: {str(e)}")

def log_zapier_event(event_type: str, data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Log Zapier event to DynamoDB"""
    
    table_name = os.environ.get('APP_TABLE')
    if not table_name:
        print("No APP_TABLE configured")
        return
    
    try:
        table = dynamodb.Table(table_name)
        
        table.put_item(
            Item={
                'app_id': f"zapier_event_{event_type}",
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'zapier_webhook_processed',
                'metadata': {
                    'event_type': event_type,
                    'data': data,
                    'result': result,
                    'processed_at': datetime.utcnow().isoformat()
                }
            }
        )
        
    except Exception as e:
        print(f"Error logging Zapier event: {str(e)}")