# Connect Workflow Architect - Complete Integration Guide

## 🎯 Objective
Connect the AI Workflow Architect to your Bridge API and Evolution Framework to achieve full system integration where all three components work together seamlessly.

**Current Status:**
- ✅ Bridge API: Running (port 3001) 
- ✅ Evolution Framework: Connected
- ❌ Workflow Architect: Not connected

**Target Status:**
- ✅ Bridge API: Running (port 3001)
- ✅ Evolution Framework: Connected  
- ✅ Workflow Architect: Connected (port 3000)

---

## 🔍 Step 1: Locate Workflow Architect

Based on your file structure, the Workflow Architect is located at:
```
projects_review/AI-Workflow-Architect.01.01.02/
```

Let's examine and prepare it for integration.

---

## 🛠️ Step 2: Prepare Workflow Architect

### 2.1 Navigate to Workflow Architect
```bash
cd projects_review/AI-Workflow-Architect.01.01.02
```

### 2.2 Check Current Configuration
```bash
# Check if package.json exists
ls -la package.json

# Check current dependencies
cat package.json | grep -A 20 '"dependencies"'

# Check for existing configuration files
ls -la .env* config* vite.config.*
```

### 2.3 Install Dependencies
```bash
# Install Node.js dependencies
npm install

# If there are any missing dependencies for integration
npm install axios ws socket.io-client
```

---

## 🔗 Step 3: Configure Integration

### 3.1 Create Environment Configuration
```bash
# Create .env file for Workflow Architect
cat > .env << EOF
# Bridge API Integration
VITE_BRIDGE_API_URL=http://localhost:3001
VITE_EVOLUTION_API_URL=http://localhost:5000
VITE_WEBSOCKET_URL=ws://localhost:3001

# Development Configuration
VITE_NODE_ENV=development
VITE_API_TIMEOUT=30000
VITE_WEBSOCKET_ENABLED=true
VITE_AUTO_CONNECT=true

# Optional: API Keys (if needed)
# VITE_OPENAI_API_KEY=your_key_here
# VITE_ANTHROPIC_API_KEY=your_key_here
EOF
```

### 3.2 Update Bridge API Configuration
```bash
# Update Bridge API to expect Workflow Architect on port 3000
cd ../../bridge-api

# Update .env file
echo "WORKFLOW_API_URL=http://localhost:3000" >> .env

# Restart Bridge API to pick up new config
# (If running in Docker, restart the container)
```

---

## 🚀 Step 4: Start Workflow Architect

### 4.1 Development Mode
```bash
cd projects_review/AI-Workflow-Architect.01.01.02

# Start in development mode
npm run dev

# This should start the Workflow Architect on port 3000
# Look for output like: "Local: http://localhost:3000"
```

### 4.2 Production Mode (Alternative)
```bash
# Build for production
npm run build

# Start production server
npm run preview
# OR
npm start
```

---

## 🔍 Step 5: Verify Integration

### 5.1 Check All Services Running
```bash
# Check Bridge API
curl http://localhost:3001/health

# Check Evolution Framework  
curl http://localhost:5000/api/status

# Check Workflow Architect
curl http://localhost:3000/health
# OR if no health endpoint exists:
curl http://localhost:3000/
```

### 5.2 Run Integration Tests
```bash
# Run the comprehensive test suite
python test_unified_system.py

# Expected output:
# ✅ PASS - Bridge API Health
# ✅ PASS - Evolution API Health  
# ✅ PASS - Workflow API Health    # <- This should now pass!
# ✅ PASS - Mutation via Bridge
# ✅ PASS - Unified Status
```

### 5.3 Check Bridge API Status
```bash
# This should now show all three systems connected
curl http://localhost:3001/health | python -m json.tool

# Expected output:
# {
#   "success": true,
#   "data": {
#     "bridge": { "status": "healthy" },
#     "evolution": { "connected": true },
#     "workflow": { "connected": true }  # <- This should now be true!
#   }
# }
```

---

## 🛠️ Step 6: Troubleshooting

### 6.1 Common Issues

**Issue: Workflow Architect won't start**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000  # Kill any processes using port 3000
```

**Issue: CORS errors in browser**
```bash
# Update Bridge API CORS settings
# Edit bridge-api/src/config/index.ts
# Add 'http://localhost:3000' to allowed origins
```

**Issue: WebSocket connection fails**
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" http://localhost:3001/
```

### 6.2 Debug Steps

**Check Workflow Architect Logs:**
```bash
# In the terminal where you ran npm run dev
# Look for error messages or connection attempts
```

**Check Bridge API Logs:**
```bash
# If running with Docker
docker-compose logs -f bridge-api

# If running directly
# Check the terminal where Bridge API is running
```

**Test Individual Connections:**
```bash
# Test Bridge API -> Workflow connection
curl -X POST http://localhost:3001/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Test Workflow -> Bridge connection (from Workflow Architect console)
fetch('http://localhost:3001/health').then(r => r.json()).then(console.log)
```

---

## 🎯 Step 7: Verify Full Integration

### 7.1 Test Cross-System Communication

**Test 1: Mutation Flow**
```bash
# Apply mutation through Bridge API
curl -X POST http://localhost:3001/api/evolution/mutate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "workflow_integration_test",
    "description": "Test mutation with workflow integration",
    "fitness_impact": 1.0,
    "source_ai": "WorkflowIntegrationTest"
  }'

# This should trigger events in all three systems
```

**Test 2: Workflow Execution**
```bash
# Execute workflow through Bridge API
curl -X POST http://localhost:3001/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "integration_test_workflow",
    "steps": [
      {"type": "test", "action": "ping"}
    ]
  }'
```

### 7.2 Monitor Real-Time Events

**Open WebSocket Connection:**
```bash
# Use a WebSocket client to monitor events
wscat -c ws://localhost:3001

# You should see real-time events flowing between systems
```

**Check Event Stream:**
```bash
# Monitor Server-Sent Events
curl -N http://localhost:3001/api/events/stream
```

---

## ✅ Step 8: Success Verification

When everything is working correctly, you should see:

### 8.1 All Services Healthy
```bash
curl http://localhost:3001/health
# Shows: bridge=healthy, evolution=connected, workflow=connected
```

### 8.2 Integration Tests Pass
```bash
python test_unified_system.py
# Result: 5/5 tests passed (including workflow tests)
```

### 8.3 Real-Time Communication
- Events flow between all three systems
- Mutations trigger workflow updates
- Workflow changes affect evolution fitness
- All systems maintain synchronized state

### 8.4 Web Interfaces Accessible
- Bridge API: http://localhost:3001 (API endpoints)
- Evolution Framework: http://localhost:5000 (Web dashboard)
- Workflow Architect: http://localhost:3000 (React interface)

---

## 🚀 Next Steps After Connection

Once Workflow Architect is connected:

1. **Update Package Creator**: Modify `create_sellable_packages.py` to include Workflow Architect in Professional+ tiers

2. **Test Full Packages**: Create and test complete packages with all three systems

3. **Update Documentation**: Ensure all guides reflect the three-system architecture

4. **Create Demo Scenarios**: Build workflows that showcase the full platform capabilities

5. **Launch Commercial Packages**: You'll now have a complete, integrated platform ready for sale

---

## 🎉 Success!

Once you complete these steps, your unified AI platform will be fully integrated with all three components working together seamlessly. This transforms your system from a two-component integration to a complete, enterprise-ready AI orchestration platform.

**Ready to connect? Let's complete the integration! 🔗**