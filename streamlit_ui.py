# streamlit_chat_app.py

import asyncio
import time
import logging

import streamlit as st
from agents.sql_agent.agent import SQL_Agent

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Session state keys
KEY_AGENT = "sql_agent"
KEY_THREAD = "sql_thread"
KEY_HISTORY = "chat_history"

INITIAL_PROMPT = (
    "Meet **PixieAI** ! \n"
    "How can I help you today?"
)

# Async helper to initialize agent
async def _init_agent_async():
    agent = await SQL_Agent().get_agent()
    return agent

# Async helper to stream response tokens
async def _stream_response_async(agent, user_text: str, thread):
    """
    Calls agent.invoke_stream and yields (token, thread) pairs.
    """
    async for stream_item in agent.invoke_stream(messages=user_text, thread=thread):
        token = stream_item.content.content
        thread = stream_item.thread
        yield token, thread

def ensure_agent():
    """
    Ensure st.session_state[KEY_AGENT] is initialized.
    """
    if KEY_AGENT not in st.session_state or st.session_state[KEY_AGENT] is None:
        try:
            agent = asyncio.run(_init_agent_async())
            st.session_state[KEY_AGENT] = agent
            st.session_state[KEY_THREAD] = None
            logger.info("SQL agent initialized.")
        except Exception as e:
            logger.exception("Failed to initialize SQL agent")
            st.error(f"Error initializing SQL agent: {e}")
            st.stop()

def stream_response(user_text: str):
    """
    Gathers tokens asynchronously, then streams them into the chat_message placeholder.
    Updates st.session_state[KEY_THREAD]. Returns full response text.
    """
    agent = st.session_state[KEY_AGENT]
    thread = st.session_state.get(KEY_THREAD, None)

    # Gather all tokens (and updated thread) via asyncio
    async def _gather_all():
        items = []
        try:
            async for token, new_thread in _stream_response_async(agent, user_text, thread):
                items.append((token, new_thread))
        except Exception as e:
            # Propagate exception
            raise
        return items

    try:
        items = asyncio.run(_gather_all())
    except Exception as e:
        logger.exception("Error during async streaming")
        st.error(f"Error during processing: {e}")
        return ""

    # Stream into the UI: one assistant message, updated incrementally
    full_resp = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        for token, new_thread in items:
            full_resp += token
            # Small delay for “typing” effect; remove or adjust as desired
            time.sleep(0.02)
            # Update the content of this assistant message
            placeholder.markdown(full_resp)
            thread = new_thread

    # After streaming, update session_state thread
    st.session_state[KEY_THREAD] = thread
    return full_resp

def main():
    st.set_page_config(page_title="PixieAI Agent", page_icon="✨")
    st.title("PixieAI 🪄")

    # Initialize history on first load
    if KEY_HISTORY not in st.session_state:
        # Each entry: dict with 'role': 'user' or 'assistant', 'text': str
        st.session_state[KEY_HISTORY] = []
        # Add initial prompt as an assistant message
        st.session_state[KEY_HISTORY].append({"role": "assistant", "text": INITIAL_PROMPT})

    # Ensure the SQL agent is initialized
    ensure_agent()

    # Display chat history using st.chat_message
    for entry in st.session_state[KEY_HISTORY]:
        role = entry["role"]
        text = entry["text"]
        # Use chat components for nicer formatting
        if role == "user":
            st.chat_message("user").markdown(text)
        else:
            st.chat_message("assistant").markdown(text)

    # Chat input: returns text when the user sends a message
    user_text = st.chat_input("Ask me anything about your data...")

    if user_text:
        # Append user message to history and display immediately
        st.session_state[KEY_HISTORY].append({"role": "user", "text": user_text})
        st.chat_message("user").markdown(user_text)

        # Stream the assistant response
        try:
            assistant_response = stream_response(user_text)
        except Exception as e:
            # In case of unexpected error
            assistant_response = f"An error occurred: {e}"
            st.chat_message("assistant").markdown(assistant_response)

        # Append assistant response to history for future reruns
        st.session_state[KEY_HISTORY].append({"role": "assistant", "text": assistant_response})

        # After sending response, scroll down automatically (Streamlit does this by default when new content is added)

if __name__ == "__main__":
    main()
