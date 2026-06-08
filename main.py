from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP 
from mcp.server import Server


mcp = FastMCP("core-rag-service")

@mcp.tool()
async def query_knowledge_base(query: str) ->str:
    return f"[Mock Response] Found standard documentaion reference for: '{query}'"


app = FastAPI(title="Repo 1: Protocol Core Data Service")

@app.get("/health")
async def health_check():
    return{
        "status": "Healthy",
        "protocol": "Dual-REST-MCP",
        "engine": "FastAPI + FastMCP"    
    }

app.mount("/", mcp.sse_app())

# def main():
#     print("Hello from core-rag-service!")


# if __name__ == "__main__":
#     main()
