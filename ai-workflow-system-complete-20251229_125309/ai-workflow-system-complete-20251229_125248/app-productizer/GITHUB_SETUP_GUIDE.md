# GitHub AI Communication Setup

## Step 1: Create GitHub Repository (Optional)

If you want to use actual GitHub Issues for AI communication:

1. Create a new repository called "ai-communication-hub"
2. Make it public or private (your choice)
3. Enable Issues in repository settings

## Step 2: Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) or `public_repo` (for public)
4. Copy the token
5. Save it as environment variable: GITHUB_TOKEN

## Step 3: Update Repository Info

Edit the ai-communication-hub.py file and update:
```python
self.repo_owner = "your-github-username"
self.repo_name = "ai-communication-hub"  # or your preferred repo name
```

## Step 4: Test GitHub Integration

Run: python test-github-integration.py

## Environment Variables Needed:
```
GITHUB_TOKEN=ghp_your_token_here
```

## Alternative: Manual Issue Creation

If you don't want to use the API, the system creates markdown templates in:
- AI_GITHUB_ISSUES/ directory
- Copy and paste these into GitHub Issues manually
