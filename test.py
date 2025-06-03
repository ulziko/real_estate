# Simple test to verify agents work
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

def test_simple_agents():
    """Test if agents can be created without errors"""
    
    print("Step 1: Creating summary agent...")
    try:
        summary_agent = LlmAgent(
            model="gemini-2.0-flash",
            name="summary_agent",
            instruction="You are an expert summarizer. Please read the following text and provide a concise summary.",
            description="Agent to summarize text",
        )
        print("✅ Summary agent created successfully!")
    except Exception as e:
        print(f"❌ Error creating summary agent: {e}")
        return None
    
    print("\nStep 2: Creating root agent with tool...")
    try:
        root_agent = LlmAgent(
            model='gemini-2.0-flash',
            name='root_agent',
            instruction="You are a helpful assistant. When the user provides text, use the summary_agent to generate a summary.",
            tools=[AgentTool(agent=summary_agent)]
        )
        print("✅ Root agent created successfully!")
    except Exception as e:
        print(f"❌ Error creating root agent: {e}")
        return None
    
    print("\nStep 3: Testing agent properties...")
    print(f"Summary agent name: {summary_agent.name}")
    print(f"Root agent name: {root_agent.name}")
    print(f"Root agent has {len(root_agent.tools) if root_agent.tools else 0} tools")
    
    print("\n✅ All agents created successfully! Ready for use with ADK CLI.")
    return root_agent

# Just run this function to test
if __name__ == "__main__":
    test_simple_agents()