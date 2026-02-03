"""
AI Agent for Todo Chatbot
Implements the OpenAI Agent that integrates with MCP tools
"""
from openai import OpenAI
import os
from typing import Dict, Any, List
from pydantic import BaseModel
import json
# Removed MCP server imports as they are not needed for direct tool calling
# The tools are imported directly from mcp.tools

# Initialize OpenAI client for Groq (will be created when needed)
def get_client():
    """
    Get OpenAI client configured for Groq
    """
    from openai import OpenAI
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

# Import MCP tools
from mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    update_task,
    delete_task,
    AddTaskArguments,
    ListTasksArguments,
    CompleteTaskArguments,
    UpdateTaskArguments,
    DeleteTaskArguments
)


def initialize_todo_agent():
    """
    Initialize the OpenAI agent with MCP tools
    """
    # Define the tools available to the agent
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task for a user",
                "parameters": AddTaskArguments.model_json_schema(),
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks for a user with optional status filtering",
                "parameters": ListTasksArguments.model_json_schema(),
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": CompleteTaskArguments.model_json_schema(),
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update task title or description",
                "parameters": UpdateTaskArguments.model_json_schema(),
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task",
                "parameters": DeleteTaskArguments.model_json_schema(),
            }
        }
    ]

    return tools


def process_chat_message(user_id: str, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Process a chat message using the OpenAI agent with MCP tools
    """
    if conversation_history is None:
        conversation_history = []

    # Initialize tools
    tools = initialize_todo_agent()

    # Prepare the conversation messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant that helps users manage their todo tasks. "
                      "Use the available tools to add, list, update, complete, or delete tasks. "
                      "Always confirm actions with the user in a friendly manner. "
                      "If a user's request is ambiguous, ask for clarification."
        }
    ]

    # Add conversation history if available
    for msg in conversation_history:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    # Add the current user message
    messages.append({
        "role": "user",
        "content": message
    })

    # Call the Groq API with tools
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Using Groq's currently recommended model
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    # Extract the response
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Process tool calls if any
    tool_results = []
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Map function names to actual functions
            function_map = {
                "add_task": lambda args: add_task(AddTaskArguments(**args)),
                "list_tasks": lambda args: list_tasks(ListTasksArguments(**args)),
                "complete_task": lambda args: complete_task(CompleteTaskArguments(**args)),
                "update_task": lambda args: update_task(UpdateTaskArguments(**args)),
                "delete_task": lambda args: delete_task(DeleteTaskArguments(**args)),
            }

            if function_name in function_map:
                try:
                    # Add user_id to the arguments if not present
                    if "user_id" not in function_args:
                        function_args["user_id"] = user_id

                    result = function_map[function_name](function_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result),
                    })
                except Exception as e:
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps({"error": str(e)}),
                    })
            else:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps({"error": f"Unknown function: {function_name}"}),
                })

        # If there were tool calls, get the final response after tool execution
        if tool_results:
            # Add tool results to messages
            messages.extend(tool_results)

            # Get the final response from the assistant
            final_client = get_client()
            final_response = final_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
            )

            assistant_reply = final_response.choices[0].message.content
        else:
            assistant_reply = response_message.content
    else:
        assistant_reply = response_message.content

    # Return the response and tool calls for logging
    return {
        "response": assistant_reply,
        "tool_calls": [tc.model_dump() for tc in tool_calls] if tool_calls else [],
    }