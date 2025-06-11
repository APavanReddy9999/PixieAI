# SQL Chat Agent Project

This project provides a conversational interface for interacting with SQL databases. Users can ask questions in natural language, and an AI-powered agent (SQL_Agent) translates these queries into SQL, executes them, and returns the results. The project offers two different web UIs: one built with Streamlit and another with Chainlit.

## Features

*   **Natural Language Queries**: Interact with your database using plain English.
*   **SQL Agent**: Powered by an `SQL_Agent` (details in `agents/sql_agent/agent.py`) that handles query understanding and SQL generation.
*   **Dual UI Support**:
    *   **Streamlit Interface (`streamlit_ui.py`)**: A "PixieAI" branded chat interface.
    *   **Chainlit Interface (`app.py`)**: Another chat interface tailored for SQL agent interactions.
*   **Streaming Responses**: Assistant responses are streamed token by token for a more interactive experience.
*   **Conversation History**: Both UIs maintain chat history for context.
*   **Session Management**: Manages agent instances and conversation threads within user sessions.

## Project Structure

```
├── agents
│   └── sql_agent
│       └── agent.py      # Core SQL Agent logic (assumed)
├── streamlit_ui.py       # Streamlit application
├── app.py                # Chainlit application
└── README.md             # This file
```
*(Note: The structure of the `agents` directory is inferred from imports.)*

## Prerequisites

*   Python 3.8+
*   Pip for package management
*   Access to a SQL database that the `SQL_Agent` can connect to.
*   Potentially API keys or other credentials for the underlying AI models used by `SQL_Agent`.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    You will likely have a `requirements.txt` file. If so, run:
    ```bash
    pip install -r requirements.txt
    ```
    Key dependencies include `streamlit`, `chainlit`, and whatever libraries `SQL_Agent` relies on.

4.  **Configure Environment Variables:**
    The `SQL_Agent` might require environment variables for database connection strings, API keys, etc. Please refer to the agent's documentation or source code for required configurations.

## Running the Application

### Streamlit UI (PixieAI)

To run the Streamlit application:
```bash
streamlit run streamlit_ui.py
```
Navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

### Chainlit UI

To run the Chainlit application:
```bash
chainlit run app.py -w
```
The `-w` flag enables auto-reloading. Navigate to the URL provided by Chainlit (usually `http://localhost:8000`).

## How it Works

Both `streamlit_ui.py` and `app.py` serve as front-ends. When a user sends a message:
1.  The UI captures the input.
2.  It ensures an `SQL_Agent` instance is initialized.
3.  The user's message is passed to the `SQL_Agent`.
4.  The agent processes the message, potentially generating and executing SQL queries.
5.  The agent streams back the response, which the UI displays incrementally.
6.  Conversation context (thread) is maintained for follow-up questions.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

Specify your project's license here (e.g., MIT, Apache 2.0). If not specified, assume it's proprietary.