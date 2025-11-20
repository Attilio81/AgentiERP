test_dynamic_sql_agent
import sys
import inspect
try:
    from datapizza.agents import Agent
    from datapizza.clients.anthropic import AnthropicClient
    from datapizza.agents.agent import StepResult
    # ClientResponse might be in datapizza.core.clients or similar, let's try to find it or just inspect what we can
    
    print("Agent class methods:")
    methods = [name for name, member in inspect.getmembers(Agent) if not name.startswith("__")]
    methods.sort()
    for name in methods:
        print(f"- {name}")

    print("\nAnthropicClient class methods:")
    methods = [name for name, member in inspect.getmembers(AnthropicClient) if not name.startswith("__")]
    methods.sort()
    for name in methods:
        print(f"- {name}")

    print("\nStepResult class properties:")
    # StepResult is likely a Pydantic model or dataclass
    try:
        for name, member in inspect.getmembers(StepResult):
            if not name.startswith("__"):
                print(f"- {name}")
    except Exception as e:
        print(f"Could not inspect StepResult: {e}")
            
except ImportError as e:
    print(f"Error importing datapizza: {e}")
except Exception as e:
    print(f"Error: {e}")
