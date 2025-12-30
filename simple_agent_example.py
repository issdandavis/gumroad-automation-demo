"""
Simple AgentCore Example
This demonstrates how to wrap an existing agent for AgentCore deployment
"""

from bedrock_agentcore import BedrockAgentCoreApp
import json
import datetime

# Create the AgentCore app instance
app = BedrockAgentCoreApp()

@app.entrypoint
def simple_agent(request_context):
    """
    A simple agent that responds to user prompts
    This is the main entry point for your agent
    """
    # Extract the prompt from the request
    prompt = request_context.get("prompt", "Hello!")
    
    # Simple response logic (in a real agent, this would call your AI model)
    if "hello" in prompt.lower():
        response = "Hello! I'm a simple AgentCore agent. How can I help you today?"
    elif "weather" in prompt.lower():
        response = "I'm a demo agent and don't have access to weather data, but I'd be happy to help with other questions!"
    elif "time" in prompt.lower():
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"The current time is: {current_time}"
    else:
        response = f"You said: '{prompt}'. I'm a simple demo agent. Try asking about hello, weather, or time!"
    
    return {
        "response": response,
        "agent_name": "SimpleAgent",
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    # For local testing
    test_request = {"prompt": "Hello there!"}
    result = simple_agent(test_request)
    print("Test Response:", json.dumps(result, indent=2))