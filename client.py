import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


async def main():
    server_url = "http://127.0.0.1:8000/sse"

    print(f"Connecting to {server_url}")
    # Establish the SSE connection (The "GET" stream) and create a ClientSession to it
    async with sse_client(server_url) as stream:
        print(f"Connected to SSE stream. Endpoint recieved.")
        # Initialize the MCP session over the established streams
        # stream[0] is the read pipe, stream[1] is the write pipe
        async with ClientSession(stream[0], stream[1]) as session:
            # Perform the mandatory JSON-RPC initialization handsake with the server
            print("Requesting JSON-RPC inisitalization handshake...")
            await session.initialize()
            print("Session initialized successfully.")

            # Execute our first command: List the available tools on the server
            # This automacically routes as a POST route request to /messages/UUID
            response = await session.list_tools()

            print("\n=== Available Tools ===")
            for tool in response.tools:
                print(f" - {tool.name}: {tool.description}")

            if not response.tools:
                print("No tools available on the server.")

if __name__ == "__main__":
    asyncio.run(main())