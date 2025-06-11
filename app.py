"""
Chainlit integration for SQL chat agent.

This module sets up a Chainlit chat interface that uses a Semantic Kernel-based
SQL agent (SQL_Agent) to handle user queries against a database.
"""

import logging
from typing import Optional

import chainlit as cl
from agents.sql_agent.agent import SQL_Agent

# Configure module-level logger
logger = logging.getLogger(__name__)

# Constants for session storage keys
SQL_AGENT_SESSION_KEY = "sql_agent"
SQL_THREAD_SESSION_KEY = "sql_thread"
INITIAL_PROMPT = (
    "🧠💬 Welcome to the **SQL Agent**! 📊🛠️\n\n"
    "Ask me any database-related question, like:\n"
    "- \"Show top 10 products by sales\"\n"
    "- \"What is the total revenue last month?\"\n\n"
    "I'm here to help you explore your data! 🔍✨"
)
ASK_USER_TIMEOUT_MS = 12000  # Timeout in milliseconds for initial prompt


@cl.on_chat_start
async def on_chat_start():
    """
    Handler invoked when a new chat session begins.

    - Initializes the SQL agent placeholder in the session.
    - Prompts the user with an initial message.
    - If the user responds, passes that response to process_and_respond().
    """
    # Initialize the agent placeholder in session
    cl.user_session.set(SQL_AGENT_SESSION_KEY, None)

    # Prompt the user to start the SQL agent interaction
    try:
        response = await cl.AskUserMessage(
            content=INITIAL_PROMPT,
            timeout=ASK_USER_TIMEOUT_MS
        ).send()
    except Exception as e:
        logger.exception("Error while asking initial user message")
        await cl.Message(content="An error occurred during startup. Goodbye.").send()
        return

    # If the user did not reply in time or response is empty, end the chat
    if not response or "output" not in response or not response["output"].strip():
        await cl.Message(content="Goodbye!").send()
        return

    # Process the first user reply
    await process_and_respond(response["output"].strip())


@cl.on_message
async def on_message(message: cl.Message):
    """
    Handler invoked for each incoming user message after chat start.

    Delegates the message content to process_and_respond().
    """
    user_text = message.content.strip()
    if not user_text:
        # Optionally handle empty messages
        await cl.Message(content="Please enter a query.").send()
        return

    await process_and_respond(user_text)


async def process_and_respond(user_text: str):
    """
    Core processing: retrieves or creates the SQL agent, sends the user_text to it,
    streams back the response tokens, and maintains conversation thread state.

    Args:
        user_text (str): The user's latest message to process.
    """
    # Retrieve or initialize the SQL agent instance in the session
    agent = cl.user_session.get(SQL_AGENT_SESSION_KEY)
    if agent is None:
        try:
            agent = await SQL_Agent().get_agent()
            cl.user_session.set(SQL_AGENT_SESSION_KEY, agent)
        except Exception as e:
            logger.exception("Failed to initialize SQL agent")
            await cl.Message(content=f"Error initializing agent: {e}").send()
            return

    # Retrieve previous conversation thread from session, if any
    thread = cl.user_session.get(SQL_THREAD_SESSION_KEY)  # type: Optional

    # Prepare a Chainlit Message to stream response tokens into
    msg = cl.Message(content="")

    try:
        # Stream the agent response. Pass in previous thread for context.
        async for stream_item in agent.invoke_stream(messages=user_text, thread=thread):
            token = stream_item.content.content
            # Stream each token back to the client
            await msg.stream_token(token)
            # Update thread reference to the latest
            thread = stream_item.thread

        # Finalize and send the full response once streaming completes
        await msg.send()

        # Save the updated thread for future context
        cl.user_session.set(SQL_THREAD_SESSION_KEY, thread)

    except Exception as e:
        # Log the exception and notify the user
        logger.exception("Error during agent.invoke_stream")
        error_msg = f"An error occurred while processing your request: {e}"
        await cl.Message(content=error_msg).send()
