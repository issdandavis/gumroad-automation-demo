# Zapier AI Communication Webhook Setup

## Step 1: Create Zapier Webhook

1. Go to https://zapier.com/app/zaps
2. Click "Create Zap"
3. Choose "Webhooks by Zapier" as trigger
4. Select "Catch Hook" 
5. Copy the webhook URL
6. Save it as environment variable: ZAPIER_AI_COMM_WEBHOOK

## Step 2: Suggested Zap Actions

### Option 1: Send to Slack
- Action: Slack - Send Channel Message
- Channel: #ai-communication
- Message: Format the AI message data

### Option 2: Add to Google Sheets
- Action: Google Sheets - Create Spreadsheet Row
- Spreadsheet: "AI Communication Log"
- Map fields: From AI, To AI, Message, Timestamp, etc.

### Option 3: Send Email Notifications
- Action: Email by Zapier - Send Outbound Email
- To: your-email@domain.com
- Subject: "New AI Communication: {{from_ai}} → {{to_ai}}"

### Option 4: Create Trello Cards
- Action: Trello - Create Card
- Board: "AI Communication Tasks"
- List: "Pending Messages"
- Card Name: "{{from_ai}} → {{to_ai}}: {{message_type}}"

### Option 5: Post to Discord
- Action: Discord - Send Channel Message
- Channel: #ai-communication
- Message: Format the AI message data

## Step 3: Test Webhook

1. Turn on your Zap
2. Run: python test-zapier-integration.py
3. Check if the webhook receives the test data

## Environment Variables Needed:
```
ZAPIER_AI_COMM_WEBHOOK=https://hooks.zapier.com/hooks/catch/your_webhook_id/
```

## Sample Webhook Payload:
```json
{
  "id": "msg_20251225_123456_Kiro",
  "timestamp": "2025-12-25T12:34:56.789",
  "from_ai": "Kiro",
  "to_ai": "ChatGPT", 
  "message": "Hello! Testing AI communication.",
  "message_type": "greeting",
  "priority": "normal",
  "status": "pending"
}
```
