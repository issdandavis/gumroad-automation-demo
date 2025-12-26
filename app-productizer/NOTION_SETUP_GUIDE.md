# Notion AI Communication Database Setup

## Step 1: Create Notion Database

1. Go to your Notion workspace
2. Create a new database called "AI Communication Hub"
3. Add these properties:

### Database Properties:
- **Title** (Title) - Message title
- **From AI** (Text) - Sending AI name
- **To AI** (Text) - Receiving AI name  
- **Message Type** (Select) - greeting, task, analysis, research, response
- **Priority** (Select) - low, normal, high, urgent
- **Status** (Select) - pending, read, responded, completed
- **Message** (Text) - Full message content
- **Timestamp** (Date) - When message was sent
- **Message ID** (Text) - Unique identifier
- **Channels Used** (Multi-select) - file_system, github, notion, zapier, email

## Step 2: Get Integration Token

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "AI Communication Hub"
4. Select your workspace
5. Copy the "Internal Integration Token"
6. Save it as environment variable: NOTION_TOKEN

## Step 3: Get Database ID

1. Open your AI Communication Hub database
2. Copy the URL - it looks like:
   https://notion.so/workspace/DATABASE_ID?v=...
3. Extract the DATABASE_ID (32 character string)
4. Save it as environment variable: NOTION_AI_COMM_DB

## Step 4: Share Database with Integration

1. In your database, click "Share" 
2. Click "Invite"
3. Search for "AI Communication Hub" (your integration)
4. Click "Invite"

## Step 5: Test Integration

Run the test script: python test-notion-integration.py

## Environment Variables Needed:
```
NOTION_TOKEN=secret_your_integration_token_here
NOTION_AI_COMM_DB=your_database_id_here
```
