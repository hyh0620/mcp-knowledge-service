# Integration / 接入指南

Any application can integrate with MCP Knowledge Service by using the official MCP Python client.

任何业务应用都可以通过官方 MCP Python Client 接入 MCP Knowledge Service。

## Client Lifecycle / Client 生命周期

The application should create MCP server parameters, start stdio transport, create `ClientSession`, call `initialize`, inspect `tools/list`, and then call `query_knowledge_hub`.

业务应用应创建 MCP server parameters，启动 stdio transport，创建 `ClientSession`，执行 `initialize`，检查 `tools/list`，再调用 `query_knowledge_hub`。

## Server Parameters / 服务参数

```python
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command="<PATH_TO_SERVICE>/.venv/bin/python",
    args=["-m", "src.mcp_server.server"],
    cwd="<PATH_TO_SERVICE>",
    env=dict(os.environ),
)
```

## Client Flow / 调用流程

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

`collection` selects the knowledge namespace. Citations should be preserved by the caller and shown when useful to users.

`collection` 用于选择知识命名空间。调用方应保留 citations，并在适合的用户界面中展示来源。

## Error Handling / 错误处理

Applications should treat MCP startup or tool-call failures as knowledge-service unavailability.

业务应用应把 MCP 启动失败或 tool 调用失败视为知识检索不可用。

Business-critical deterministic rules should not silently depend on retrieval output.

关键业务规则不应静默依赖检索结果。例如价格、时长、库存、排班或交易成功条件应由业务系统自己的确定性规则决定。

## Security Boundary / 安全边界

This public service does not claim authentication, authorization, tenant isolation, or production security controls.

当前公开范围不声明认证、授权、租户隔离或生产级安全控制。

Do not log API keys, raw secrets, or full sensitive user inputs.

不要记录 API Key、原始密钥或完整敏感用户输入。
