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

    # Debug logging
    print(f"DEBUG: User message: {message}")
    print(f"DEBUG: Agent response: {response_message}")
    print(f"DEBUG: Tool calls: {tool_calls}")

    # Check if the message intent suggests a CRUD operation but no tool was called
    message_lower = message.lower()
    crud_keywords = ["add", "create", "delete", "remove", "edit", "update", "complete", "finish", "done"]
    has_crud_intent = any(keyword in message_lower for keyword in crud_keywords)

    print(f"DEBUG: Has CRUD intent: {has_crud_intent}, Tool calls exist: {bool(tool_calls)}")

    if has_crud_intent and not tool_calls:
        # Force tool usage by retrying with a stricter system prompt
        strict_system_prompt = {
            "role": "system",
            "content": "You are a helpful AI assistant that helps users manage their todo tasks. "
                      "USE THE AVAILABLE TOOLS to add, list, update, complete, or delete tasks. "
                      "If the user wants to add, create, delete, edit, update, complete, or remove a task, "
                      "YOU MUST USE THE APPROPRIATE TOOL. Do not respond without using tools for these operations."
        }

        # Reconstruct messages with the stricter system prompt
        strict_messages = [strict_system_prompt]
        for msg in conversation_history:
            strict_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        strict_messages.append({
            "role": "user",
            "content": message
        })

        # Retry with stricter prompt
        print(f"DEBUG: Retrying with stricter prompt due to CRUD intent without tool calls")
        strict_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=strict_messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = strict_response.choices[0].message
        tool_calls = response_message.tool_calls

        # Debug logging after retry
        print(f"DEBUG: After retry - Agent response: {response_message}")
        print(f"DEBUG: After retry - Tool calls: {tool_calls}")

    # Process tool calls if any
    tool_results = []
    if tool_calls:
        print(f"DEBUG: Processing {len(tool_calls)} tool calls")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            print(f"DEBUG: Executing tool '{function_name}' with args: {function_args}")

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
                    print(f"DEBUG: Tool '{function_name}' executed successfully, result: {result}")
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result),
                    })
                except Exception as e:
                    print(f"DEBUG: Error executing tool '{function_name}': {str(e)}")
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps({"error": str(e)}),
                    })
            else:
                print(f"DEBUG: Unknown function: {function_name}")
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