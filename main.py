import uvicorn
from fastapi import FastAPI
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# 1. Initialize Bare-Metal Objects
app = FastAPI(title="Core RAG Service")
mcp = Server("core-rag-service")

# 2. Global Transport Layer
# This handles the session multiplexing internally so we don't need a global dictionary
transport = SseServerTransport("/messages/")

# 3. REST Protocol: Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "Healthy",
        "protocol": "Dual-REST-MCP",
        "model" : "Qwen3.5-4B-AWQ",
        "vram_cap": "0.6"   
    }

# 4. MCP Protocol: SSE Transport Stream (Strict ASGI)
async def sse_asgi(scope, receive, send):
    # Connects the raw socket directly to the MCP event loop
    async with transport.connect_sse(scope, receive, send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())

# 5. MCP Protocol: Message Receiver (Strict ASGI)
async def messages_asgi(scope, receive, send):
    # Dumps incoming POST bytes directly into the transport layer
    await transport.handle_post_message(scope, receive, send)

# 6. Bypass FastAPI HTTP Routers completely for MCP
app.mount("/sse", sse_asgi)
app.mount("/messages", messages_asgi)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)