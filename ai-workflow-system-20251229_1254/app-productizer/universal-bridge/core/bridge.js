#!/usr/bin/env node
/**
 * Universal Bridge - JavaScript/Node.js Implementation
 * Connects JavaScript applications to the Universal Bridge
 */

const fs = require('fs').promises;
const path = require('path');
const WebSocket = require('ws');
const http = require('http');
const crypto = require('crypto');

class UniversalMessage {
    constructor(messageType, sourceLanguage, targetLanguage = 'universal', payload = {}, responseChannel = 'websocket') {
        this.id = crypto.randomUUID();
        this.timestamp = new Date().toISOString();
        this.messageType = messageType;
        this.sourceLanguage = sourceLanguage;
        this.targetLanguage = targetLanguage;
        this.payload = payload;
        this.responseChannel = responseChannel;
        this.checksum = this.calculateChecksum();
    }

    calculateChecksum() {
        const content = `${this.id}${this.timestamp}${this.messageType}${JSON.stringify(this.payload, Object.keys(this.payload).sort())}`;
        return crypto.createHash('md5').update(content).digest('hex');
    }

    toJSON() {
        return {
            id: this.id,
            timestamp: this.timestamp,
            message_type: this.messageType,
            source_language: this.sourceLanguage,
            target_language: this.targetLanguage,
            payload: this.payload,
            response_channel: this.responseChannel,
            checksum: this.checksum
        };
    }

    toString() {
        return JSON.stringify(this.toJSON(), null, 2);
    }

    static fromJSON(jsonStr) {
        const data = JSON.parse(jsonStr);
        const msg = new UniversalMessage(
            data.message_type,
            data.source_language,
            data.target_language,
            data.payload,
            data.response_channel
        );
        
        msg.id = data.id;
        msg.timestamp = data.timestamp;
        
        // Verify checksum
        if (msg.checksum !== data.checksum) {
            throw new Error('Message checksum mismatch - data may be corrupted');
        }
        
        return msg;
    }
}

class JavaScriptBridge {
    constructor(bridgeUrl = 'ws://localhost:8765') {
        this.bridgeUrl = bridgeUrl;
        this.websocket = null;
        this.messageHandlers = new Map();
        this.pendingMessages = new Map();
        this.isConnected = false;
        
        this.connect();
    }

    async connect() {
        try {
            console.log('🔌 Connecting to Universal Bridge...');
            
            // For now, use file system communication
            await this.ensureDirectories();
            this.startFileWatcher();
            
            this.isConnected = true;
            console.log('✅ Connected to Universal Bridge');
            
        } catch (error) {
            console.error('❌ Failed to connect to Universal Bridge:', error);
        }
    }

    async ensureDirectories() {
        const dirs = [
            'bridge_messages/javascript',
            'bridge_messages/incoming',
            'bridge_messages/outgoing'
        ];
        
        for (const dir of dirs) {
            await fs.mkdir(dir, { recursive: true });
        }
    }

    startFileWatcher() {
        // Watch for incoming messages
        setInterval(async () => {
            try {
                const incomingDir = 'bridge_messages/javascript';
                const files = await fs.readdir(incomingDir);
                
                for (const file of files) {
                    if (file.endsWith('.json')) {
                        const filePath = path.join(incomingDir, file);
                        const content = await fs.readFile(filePath, 'utf8');
                        
                        try {
                            const message = UniversalMessage.fromJSON(content);
                            await this.handleIncomingMessage(message);
                            
                            // Move to processed
                            const processedDir = path.join(incomingDir, 'processed');
                            await fs.mkdir(processedDir, { recursive: true });
                            await fs.rename(filePath, path.join(processedDir, file));
                            
                        } catch (error) {
                            console.error(`❌ Error processing message ${file}:`, error);
                        }
                    }
                }
            } catch (error) {
                // Directory might not exist yet
            }
        }, 1000);
    }

    async handleIncomingMessage(message) {
        console.log(`📥 Received message: ${message.id} (${message.messageType})`);
        
        const handler = this.messageHandlers.get(message.messageType);
        if (handler) {
            try {
                await handler(message);
            } catch (error) {
                console.error(`❌ Error handling message ${message.id}:`, error);
            }
        } else {
            console.log(`⚠️ No handler for message type: ${message.messageType}`);
        }
    }

    async sendMessage(message) {
        if (!this.isConnected) {
            throw new Error('Not connected to Universal Bridge');
        }

        // Send via file system
        const outgoingPath = path.join('bridge_messages/incoming', `${message.id}.json`);
        await fs.writeFile(outgoingPath, message.toString());
        
        console.log(`📤 Message sent: ${message.id} (${message.sourceLanguage} → ${message.targetLanguage})`);
        return message.id;
    }

    onMessage(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
        console.log(`📝 Registered handler for ${messageType}`);
    }

    // Convenience methods for common operations
    async requestAI(prompt, instructions = '', context = {}) {
        const message = new UniversalMessage(
            'ai_request',
            'javascript',
            'universal',
            {
                action: 'generate_content',
                prompt: prompt,
                instructions: instructions,
                context: context
            },
            'file_system'
        );

        return await this.sendMessage(message);
    }

    async translateCode(code, targetLanguage) {
        const message = new UniversalMessage(
            'code_translation',
            'javascript',
            targetLanguage,
            { code: code },
            'file_system'
        );

        return await this.sendMessage(message);
    }

    async callFunction(targetLanguage, functionName, args = [], kwargs = {}) {
        const message = new UniversalMessage(
            'function_call',
            'javascript',
            targetLanguage,
            {
                function_name: functionName,
                args: args,
                kwargs: kwargs
            },
            'file_system'
        );

        return await this.sendMessage(message);
    }

    // JavaScript-specific AI helpers
    async generateJSFunction(description, parameters = []) {
        return await this.requestAI(
            `Generate a JavaScript function: ${description}`,
            `Parameters: ${parameters.join(', ')}. Return only the function code.`,
            { language: 'javascript', type: 'function_generation' }
        );
    }

    async optimizeJSCode(code) {
        return await this.requestAI(
            `Optimize this JavaScript code: ${code}`,
            'Focus on performance, readability, and best practices. Return only the optimized code.',
            { language: 'javascript', type: 'code_optimization' }
        );
    }

    async generateJSTests(code) {
        return await this.requestAI(
            `Generate Jest tests for this JavaScript code: ${code}`,
            'Create comprehensive unit tests with edge cases. Use Jest framework.',
            { language: 'javascript', type: 'test_generation' }
        );
    }
}

// Demo usage
async function demoJavaScriptBridge() {
    console.log('🌍 JAVASCRIPT UNIVERSAL BRIDGE DEMO');
    console.log('=' .repeat(50));
    
    const bridge = new JavaScriptBridge();
    
    // Wait for connection
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Set up message handlers
    bridge.onMessage('ai_response', async (message) => {
        console.log('🤖 AI Response received:', message.payload);
    });
    
    bridge.onMessage('code_translation', async (message) => {
        console.log('🔄 Code translation received:', message.payload);
    });
    
    // Demo 1: AI request
    console.log('\n🤖 Demo 1: AI Request from JavaScript');
    await bridge.requestAI(
        'Create a JavaScript function that validates email addresses',
        'Use modern ES6+ syntax and include error handling',
        { project: 'App Productizer', priority: 'high' }
    );
    
    // Demo 2: Code translation
    console.log('\n🔄 Demo 2: Translate JavaScript to Python');
    const jsCode = `
function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
}
`;
    
    await bridge.translateCode(jsCode, 'python');
    
    // Demo 3: Function call to Python
    console.log('\n📞 Demo 3: Call Python function from JavaScript');
    await bridge.callFunction(
        'python',
        'generate_documentation',
        [jsCode],
        { format: 'markdown', include_examples: true }
    );
    
    // Demo 4: JavaScript-specific AI helpers
    console.log('\n⚡ Demo 4: JavaScript-specific AI helpers');
    await bridge.generateJSFunction(
        'A function that debounces user input',
        ['callback', 'delay']
    );
    
    await bridge.optimizeJSCode(`
function slowFunction(arr) {
    let result = [];
    for (let i = 0; i < arr.length; i++) {
        for (let j = 0; j < arr.length; j++) {
            if (arr[i] === arr[j] && i !== j) {
                result.push(arr[i]);
            }
        }
    }
    return result;
}
`);
    
    console.log('\n✅ JavaScript Bridge Demo Complete');
    console.log('📁 Check bridge_messages/ directory for message files');
}

// Export for use as module
module.exports = { UniversalMessage, JavaScriptBridge };

// Run demo if called directly
if (require.main === module) {
    demoJavaScriptBridge().catch(console.error);
}