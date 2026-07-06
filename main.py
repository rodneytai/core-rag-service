import uvicorn
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types as types

app = FastAPI(title="Core RAG Service")
mcp = Server("core-rag-service")

transport = SseServerTransport("/messages")

# 1. Register a tool to enable MCP tools capability
@mcp.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="check_vram",
            description="Check the current VRAM usage of the local GPU.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
@app.get('/health')
async def health_check():
    return {
        "status": "Healthy",
        "message": "FastAPI server is running",
        "code": 200,
        "model": "Qwen3.5-4B-AWQ",
        "protocol": "FastAPI + MCP"
    }

async def sse_endpoint(request: Request):
    async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())

# 2. Pure ASGI wrapper to silence Starlette's NoneType traceback
async def messages_app(scope, receive, send):
    await transport.handle_post_message(scope, receive, send)

app.add_route("/sse", sse_endpoint, methods=["GET"])
app.mount("/messages", messages_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
