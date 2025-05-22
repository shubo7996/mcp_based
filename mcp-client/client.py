# ollama_client.py
import aiohttp
import asyncio
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.agent.workflow import ToolCallResult, ToolCall
from llama_index.core.workflow import Context

# Initialize Ollama LLM
llm = Ollama(model="llama3.2", request_timeout=120.0)
Settings.llm = llm

# System prompt

SYSTEM_PROMPT_SQLITE = """\
You are a helpful assistant with access to a database of people.
You can use the following tools to interact with the database:

1. add_data:
   - Add a new person to the database.
   - Accepts a full SQL INSERT query.
   - Example:
     INSERT INTO people (name, age, profession)
     VALUES ('Alice Smith', 25, 'Developer')

2. read_data:
   - Retrieve data from the people table.
   - Accepts a SQL SELECT query or defaults to: SELECT * FROM people
   - Example:
     SELECT name, age FROM people WHERE age > 30

3. update_people:
   - Update existing records in the people table.
   - Accepts a SQL UPDATE query.
   - Example:
     UPDATE people SET age = 27 WHERE name = 'Subhamoy'

4. delete_person:
   - Delete a person’s record from the table.
   - Accepts a SQL DELETE query.
   - Example:
     DELETE FROM people WHERE name = 'Alice Smith'

Always write well-formed SQL queries when calling these tools. 
Use them when the user asks to add, read, update, or delete any person-related information.
"""

SYSTEM_PROMPT_NEWS = """\
You are an AI assistant with access to these tools:

1. Wikipedia Tools:
   - get_wikipedia_summary: Get summaries of topics from Wikipedia

2. News Tools:
   - get_latest_news: Get current news headlines from NPR or BBC

3. Stock Tools:
   - get_stock_news: Get recent news about specific stocks

Use these tools when appropriate to answer user questions.
"""

async def detect_running_server():
    """Check which MCP server is running (8000 or 8001)"""
    ports_to_try = [8000, 8001]
    timeout = aiohttp.ClientTimeout(total=2)  # 2 second timeout per check
    
    async with aiohttp.ClientSession() as session:
        for port in ports_to_try:
            try:
                url = f"http://127.0.0.1:{port}/sse"
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return port
            except:
                continue
    return None

async def get_agent(tools: McpToolSpec, system_prompt: str):
    """Create and return a FunctionAgent with the specified tools"""
    tools_list = await tools.to_tool_list_async()
    for tool in tools_list:
        print(tool.metadata.name, tool.metadata.description)
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with Our Database software.",
        tools=tools_list,
        llm=llm,
        system_prompt=system_prompt,
    )
    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    """Handle user messages with the agent"""
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)

async def main():
    """Main async function to run the agent"""
    running_port = await detect_running_server()
    if not running_port:
        print("Error: No MCP server found running on ports 8000 or 8001")
        return

    print(f"Connected to MCP server on port {running_port}")
    # Initialize MCP client and tools
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_tool = McpToolSpec(client=mcp_client)

    # Get the agent
    if running_port==8000:
        agent = await get_agent(mcp_tool, system_prompt=SYSTEM_PROMPT_SQLITE)
    else:
        agent = await get_agent(mcp_tool, system_prompt=SYSTEM_PROMPT_NEWS)
        
    agent_context = Context(agent)

    # Interactive loop
    while True:
        user_input = input("Enter your message (type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
            
        print("User: ", user_input)
        response = await handle_user_message(
            user_input, agent, agent_context, verbose=True
        )
        print("Agent: ", response)

if __name__ == "__main__":
    # Apply nest_asyncio for Jupyter-like async behavior
    import nest_asyncio
    nest_asyncio.apply()
    
    # Run the main async function
    asyncio.run(main())