"""
Hugging Face Space wrapper for the Todo Chatbot API
This file creates a Gradio interface that can run on Hugging Face Spaces
while preserving the original FastAPI backend functionality.
"""
import gradio as gr
import uvicorn
import os
from contextlib import asynccontextmanager
from typing import List
import sys
import threading
import time

# Add the current directory to the path so we can import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the core functionality from the existing modules
from main import app as fastapi_app
from models import User, Task, Conversation, Message, UserCreate, LoginRequest, UserResponse
from db import get_session, create_db_and_tables
from agents.todo_agent import process_chat_message
from middleware.auth import create_access_token, verify_token

# Use SQLite for Hugging Face Spaces
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./todo_hf_space.db"

# Initialize database
create_db_and_tables()

def create_gradio_interface():
    """Create Gradio interface for the Todo Chatbot"""

    def chat_interface(message: str, history: List) -> str:
        """
        Process chat messages using the AI agent
        This simulates the chat API functionality in a Gradio interface
        """
        # For demo purposes, we'll simulate a user session
        # In a real implementation, you'd handle user authentication

        # Simulate user ID (in production, this would come from auth)
        user_id = "1"  # Demo user

        # Convert Gradio history to the format expected by the AI agent
        conversation_history = []
        for user_msg, assistant_msg in history:
            conversation_history.append({"role": "user", "content": user_msg})
            if assistant_msg:
                conversation_history.append({"role": "assistant", "content": assistant_msg})

        try:
            # Process the message with the AI agent
            result = process_chat_message(
                user_id=user_id,
                message=message,
                conversation_history=conversation_history
            )

            # Store the conversation in the database
            with get_session() as session:
                # Create or get conversation
                conversation = Conversation(user_id=int(user_id))
                session.add(conversation)
                session.commit()
                session.refresh(conversation)

                # Store user message
                user_msg_obj = Message(
                    conversation_id=conversation.id,
                    role="user",
                    content=message
                )
                session.add(user_msg_obj)

                # Store assistant response
                assistant_msg_obj = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=result["response"]
                )
                session.add(assistant_msg_obj)

                session.commit()

            return result["response"]
        except Exception as e:
            return f"Error processing message: {str(e)}"

    def todo_management_interface(command: str) -> str:
        """
        Interface for direct todo management commands
        """
        # Simulate user ID (in production, this would come from auth)
        user_id = "1"  # Demo user

        try:
            # Process the command using the AI agent
            result = process_chat_message(
                user_id=user_id,
                message=command,
                conversation_history=[]
            )

            return result["response"]
        except Exception as e:
            return f"Error processing command: {str(e)}"

    with gr.Blocks(title="AI-Powered Todo Chatbot") as demo:
        gr.Markdown("# 📝 AI-Powered Todo Chatbot")
        gr.Markdown("Chat with the AI assistant to manage your tasks using natural language!")

        with gr.Tab("Chat Interface"):
            chatbot = gr.Chatbot(label="Chat with the AI Assistant")
            msg = gr.Textbox(label="Your message")
            clear = gr.Button("Clear")

            msg.submit(chat_interface, [msg, chatbot], chatbot).then(
                lambda: "", None, msg  # Clear the input textbox after submission
            )

        with gr.Tab("Direct Commands"):
            command_input = gr.Textbox(label="Enter your command", placeholder="e.g., Add buy groceries, Show my tasks, etc.")
            command_output = gr.Textbox(label="Response", interactive=False)
            command_btn = gr.Button("Execute Command")

            command_btn.click(todo_management_interface, command_input, command_output)

        with gr.Tab("Instructions"):
            gr.Markdown("""
            ### How to use:
            - **Chat Interface**: Type your requests in natural language
            - **Direct Commands**: Enter specific commands

            ### Examples:
            - "Add buy groceries to my tasks"
            - "Show me all my tasks"
            - "Mark task 1 as completed"
            - "Update task 1 to 'buy organic groceries'"
            - "Delete task 2"
            """)

    return demo

# Create the Gradio interface
interface = create_gradio_interface()

if __name__ == "__main__":
    # Launch with uvicorn to serve both FastAPI endpoints and Gradio interface
    import nest_asyncio
    nest_asyncio.apply()

    # Run the Gradio app which will include the FastAPI endpoints
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        debug=True,
        share=False  # Set to True if you want a public URL
    )