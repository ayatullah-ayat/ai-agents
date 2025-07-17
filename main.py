import os
import json

from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any

from goals import Goal
from action import Action, ActionRegistry
from memory import Memory
from agent_language import AgentLanguage, AgentFunctionCallingActionLanguage
from agent import Agent
from environment import Environment
from prompt import Prompt

from groq import Groq


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

model= "llama-3.3-70b-versatile"

# ---------------------------
# Generate LLM Response
# ---------------------------
def generate_response(prompt: Prompt) -> str:
    """Call LLM to get response"""

    messages = prompt.messages
    tools = prompt.tools

    print(f"Messages: {messages}")
    print(f"Tools: {tools}")

    result = None

    if not tools:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024
        )
        result = response.choices[0].message.content
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            max_tokens=1024
        )

        print(f"Response: {response.choices[0]}")

        if response.choices[0].message.tool_calls:
            tool = response.choices[0].message.tool_calls[0]
            args = tool.function.arguments
            if args is None:
                parsed_args = {}
            else:
                parsed_args = json.loads(args)
            result = {
                "tool": tool.function.name,
                "args": parsed_args,
            }
            result = json.dumps(result)
        else:
            result = response.choices[0].message.content


    return result

if __name__ == "__main__":
    # Define the agent's goals
    goals = [
        Goal(priority=1, name="Gather Information", description="Get files list using tools and then Read each file in the project"),
        Goal(priority=2, name="Terminate", description="Call the terminate call when you have read all the files "
                                                       "and provide the content of the README in the terminate message")
    ]

    # Define the agent's language
    agent_language = AgentFunctionCallingActionLanguage()

    def read_project_file(name: str) -> str:
        with open(name, "r") as f:
            return f.read()

    def list_project_files() -> List[str]:
        return sorted([file for file in os.listdir(".") if file.endswith(".py")])


    # Define the action registry and register some actions
    action_registry = ActionRegistry()
    action_registry.register(Action(
        name="list_project_files",
        function=list_project_files,
        description="Lists all files in the project.",
        parameters={},
        terminal=False
    ))
    action_registry.register(Action(
        name="read_project_file",
        function=read_project_file,
        description="Reads a file from the project.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        },
        terminal=False
    ))
    action_registry.register(Action(
        name="terminate",
        function=lambda message: f"{message}\nTerminating...",
        description="Terminates the session and prints the message to the user.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": []
        },
        terminal=True
    ))

    # Define the environment
    environment = Environment()

    # Create an agent instance
    agent = Agent(goals, agent_language, action_registry, generate_response, environment)

    # Run the agent with user input
    user_input = "List the files in the project and read each file's content."
    final_memory = agent.run(user_input)

    # Print the final memory
    print(f"{final_memory.get_memories()}")
