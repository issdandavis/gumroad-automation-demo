"""
Notification Handler Lambda
Sends notifications via various channels
"""

import json
import requests
import os
from datetime import datetime
from typing import Dict, Any

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handle SNS notifications and send to appropriate channels
    """
    try:
        # Parse SNS message
        if 'Records' in event:
            for record in event['Records']:
                if record.get('EventSource') == 'aws:sns':
                    message = json.loads(record['Sns']['Message'])
                    process_notification(message)
        else:
            # Direct invocation
            process_notification(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Notifications sent successfully'})
        }
        
    except Exception as e:
        print(f"Error sending notifications: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_notification(message: Dict[str, Any]) -> None:
    """Process and send notification"""
    
    # Extract notification details
    source = message.get('source', 'aws.codebuild')
    detail_type = message.get('detail-type', 'Build State Change')
    detail = message.get('detail', {})
    
    if source == 'aws.codebuild':
        handle_build_notification(detail_type, detail)
    else:
        handle_generic_notification(source, detail_type, detail)

def handle_build_notification(detail_type: str, detail: Dict[str, Any]) -> None:
    """Handle CodeBuild notifications"""
    
    build_status = detail.get('build-status', 'UNKNOWN')
    project_name = detail.get('project-name', 'Unknown Project')
    build_id = detail.get('build-id', 'Unknown Build')
    
    # Create notification message
    if build_status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
        title = f"🚨 Build Failed: {project_name}"
        message = f"Build {build_id} failed with status: {build_status}"
        color = "danger"
    elif build_status == 'SUCCEEDED':
        title = f"✅ Build Succeeded: {project_name}"
        message = f"Build {build_id} completed successfully"
        color = "good"
    else:
        title = f"ℹ️ Build Update: {project_name}"
        message = f"Build {build_id} status: {build_status}"
        color = "warning"
    
    # Send to Zapier for further processing
    send_zapier_notification({
        'type': 'build_notification',
        'title': title,
        'message': message,
        'color': color,
        'project_name': project_name,
        'build_id': build_id,
        'build_status': build_status,
        'timestamp': datetime.utcnow().isoformat()
    })

def handle_generic_notification(source: str, detail_type: str, detail: Dict[str, Any]) -> None:
    """Handle generic notifications"""
    
    title = f"📢 {source}: {detail_type}"
    message = f"Event details: {json.dumps(detail, indent=2)}"
    
    send_zapier_notification({
        'type': 'generic_notification',
        'title': title,
        'message': message,
        'source': source,
        'detail_type': detail_type,
        'detail': detail,
        'timestamp': datetime.utcnow().isoformat()
    })

def send_zapier_notification(notification: Dict[str, Any]) -> None:
    """Send notification to Zapier"""
    
    webhook_url = os.environ.get('ZAPIER_WEBHOOK_URL')
    if not webhook_url:
        print("No Zapier webhook URL configured")
        return
    
    try:
        payload = {
            'trigger': 'notification',
            'notification': notification
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Notification sent to Zapier: {notification['title']}")
        else:
            print(f"Failed to send notification: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending notification to Zapier: {str(e)}")