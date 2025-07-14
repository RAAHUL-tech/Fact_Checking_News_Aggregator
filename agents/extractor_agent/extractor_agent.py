from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a.mcp import FastMCPAgent
import yaml

class ExtractorAgent(A2AServer, FastMCPAgent):
    """An agent that extracts factual claims using MCP tools."""

    def __init__(self):
        # Load configuration
        with open("agents/extractor_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

        mcp_host = self.config.get("mcp_host", "localhost")
        mcp_port = self.config.get("mcp_port", 8000)
        mcp_url = f"http://{mcp_host}:{mcp_port}"

        # Init both parents
        A2AServer.__init__(self)
        FastMCPAgent.__init__(self, mcp_servers={"factcheck": mcp_url})

    async def handle_message_async(self, message):
        """Handles incoming A2A messages and routes them to the extract_claims MCP tool."""
        try:
            if message.content.type == "text":
                input_text = message.content.text.strip()

                # Call MCP extract_claims tool
                result = await self.call_mcp_tool("factcheck", "extract_claims", text=input_text)

                return Message(
                    content=TextContent(text=f"Extracted Claims:\n{result}"),
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
