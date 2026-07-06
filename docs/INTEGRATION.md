# Integration

Any application can integrate with MCP Knowledge Service by using the official MCP Python client.

## Server Parameters

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command="<PATH_TO_SERVICE>/.venv/bin/python",
    args=["-m", "src.mcp_server.server"],
    cwd="<PATH_TO_SERVICE>",
    env=dict(os.environ),
)
```

## Client Flow

```python
async with stdio_client(params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            "query_knowledge_hub",
            {
                "query": "What does the policy say?",
                "top_k": 4,
                "collection": "knowledge_hub",
            },
        )
```

## Error Handling

Applications should treat MCP startup or tool-call failures as knowledge-service unavailability. Business-critical deterministic rules should not silently depend on retrieval output.

## Security

Do not log API keys, raw secrets, or full sensitive user inputs.
