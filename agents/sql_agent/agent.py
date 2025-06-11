import os
from dotenv import load_dotenv
from semantic_kernel.functions import KernelArguments
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPSsePlugin
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.agents import ChatCompletionAgent,ChatHistoryAgentThread
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
from plugins.sql_plugin import SqlPlugin
from semantic_kernel.services.kernel_services_extension import DEFAULT_SERVICE_NAME

load_dotenv()
chat_completion = GoogleAIChatCompletion(gemini_model_id="gemini-1.5-flash",api_key=os.getenv("GOOGLE_API_KEY"),service_id=DEFAULT_SERVICE_NAME)
AGENT_NAME ="Sql_Agent"

class SQL_Agent:
    async def get_agent(self):
        agent_kernal = Kernel()
        agent_kernal.add_service(chat_completion)
        settings = agent_kernal.get_prompt_execution_settings_from_service_id(chat_completion.service_id)
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        agent_prompt = """ you are name is PixieAI and you are personal assistant for the databases  and also you will help with the general question for the user
                        - when user greets- first introduce yourself and then greet the user ask the questions or user name.
                        You are a SQL agent. You have access to a plugin named "SQL" with two functions:
                          1) get_schema(): returns the database schema as JSON.
                          2) query_select(sql_query: str): executes a read-only SELECT query and returns rows.
                        
                        When the user asks for any data, you must:
                          - Determine the correct SELECT statement.
                          - Call the function SQL.query_select with that statement.
                          - Receive the rows and then format them (e.g., as a markdown table or JSON) in your response.
                        
                        Do NOT answer by guessing or describing schema; always invoke get_schema or query_select as needed. Example:
                          User: "Show me top 10 records from sales table"
                          Agent should call: SQL.query_select(sql_query="SELECT * FROM sales LIMIT 10;")
                        Then format and return the actual rows.
                        
                        If the user asks about schema, call SQL.get_schema(). Always check schema first if unsure of column names.
                        
                        Always validate table/column names against schema; if table not found, respond with an error message.
                        
                        Format the final output clearly (e.g., a markdown table with headers).
                        
                        Begin.
        """
        agent_kernal.add_plugin(SqlPlugin(), plugin_name="SQL")

        agent = ChatCompletionAgent(
            kernel=agent_kernal,
            name=AGENT_NAME,
            instructions=agent_prompt,
            arguments=KernelArguments(settings=settings),
        )

        return agent
    async def run(self):
        sql_agent = await self.get_agent()
        thread: ChatHistoryAgentThread | None = None
        while True:
            user_input =input("Enter something:")
            async for response in sql_agent.invoke(messages=user_input, thread=thread):
                print(f"{response.content}")
                thread= response.thread
if __name__ == "__main__":
    import asyncio
    asyncio.run(SQL_Agent().run())