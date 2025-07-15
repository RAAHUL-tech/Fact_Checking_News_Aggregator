from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
import yaml
import asyncio
import aiohttp
import json

class ExtractorAgent(A2AServer):
    """An agent that extracts factual claims using MCP tools."""

    def __init__(self):
        # Load configuration
        with open("agents/extractor_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

        mcp_host = self.config.get("mcp_host", "localhost")
        mcp_port = self.config.get("mcp_port", 8000)
        self.mcp_url = f"http://{mcp_host}:{mcp_port}"
        print(f"[ExtractorAgent] Connecting to MCP server at: {self.mcp_url}")

        # Init parent
        A2AServer.__init__(self)

    def handle_message(self, message):
        """Synchronous handler that calls the async handler."""
        print("[ExtractorAgent] handle_message called (sync)")
        return asyncio.run(self.handle_message_async(message))

    async def call_mcp_tool(self, tool_name, **kwargs):
        """Call MCP tool directly via HTTP."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.mcp_url}/tools/{tool_name}"
                payload = kwargs
                
                print(f"[ExtractorAgent] Calling MCP tool {tool_name} with payload: {payload}")
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"[ExtractorAgent] MCP tool {tool_name} result: {result}")
                        
                        # Extract all text content from the MCP response
                        if result.get("content") and len(result["content"]) > 0:
                            # Collect all text items from the content array
                            text_items = []
                            for content_item in result["content"]:
                                if content_item.get("type") == "text":
                                    text_items.append(content_item.get("text", ""))
                            
                            if text_items:
                                print(f"[ExtractorAgent] Extracted {len(text_items)} text items: {text_items}")
                                return text_items
                            else:
                                return "No text content found in MCP response"
                        else:
                            return "No content in MCP response"
                    else:
                        error_text = await response.text()
                        print(f"[ExtractorAgent] MCP tool {tool_name} failed: {response.status} - {error_text}")
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            print(f"[ExtractorAgent] Exception calling MCP tool {tool_name}: {e}")
            return f"Exception: {str(e)}"

    async def handle_message_async(self, message):
        print("[ExtractorAgent] handle_message_async called with:", message.content)
        try:
            if message.content.type == "text":
                input_text = message.content.text.strip()

                # Call MCP extract_claims tool
                result = await self.call_mcp_tool("extract_claims", text=input_text)

                # Handle the result - it's now a list of claim strings
                if isinstance(result, list):
                    return Message(
                        content=TextContent(text=json.dumps(result, indent=2)),
                        role=MessageRole.AGENT,
                        parent_message_id=message.message_id,
                        conversation_id=message.conversation_id
                    )
                else:
                    return Message(
                        content=TextContent(text=f"Unexpected result format: {result}"),
                        role=MessageRole.AGENT,
                        parent_message_id=message.message_id,
                        conversation_id=message.conversation_id
                    )

            # Fallback/default response
            return Message(
                content=TextContent(text="Please send plain text to extract factual claims."),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        except Exception as e:
            return Message(
                content=TextContent(text=f"[ExtractorAgent Error] {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

# Run the server
if __name__ == "__main__":
    agent = ExtractorAgent()
    run_server(agent, host="0.0.0.0", port=5002)
