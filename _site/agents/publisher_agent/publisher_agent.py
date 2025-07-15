from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server, A2AClient
import yaml
import json
import asyncio
import aiohttp

class PublisherAgent(A2AServer):
    """Agent that publishes verified facts to a Jekyll blog using MCP."""

    def __init__(self):
        # Load config from file
        with open("agents/publisher_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

        mcp_host = self.config.get("mcp_host", "localhost")
        mcp_port = self.config.get("mcp_port", 8000)
        self.mcp_url = f"http://{mcp_host}:{mcp_port}"
        print(f"[PublisherAgent] Connecting to MCP server at: {self.mcp_url}")

        # Initialize parent
        A2AServer.__init__(self)

    def handle_message(self, message):
        """Synchronous handler that calls the async handler."""
        print("[PublisherAgent] handle_message called (sync)")
        return asyncio.run(self.handle_message_async(message))

    async def call_mcp_tool(self, tool_name, **kwargs):
        """Call MCP tool directly via HTTP."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.mcp_url}/tools/{tool_name}"
                payload = kwargs
                
                print(f"[PublisherAgent] Calling MCP tool {tool_name} with payload: {payload}")
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"[PublisherAgent] MCP tool {tool_name} result: {result}")
                        return result.get("content", [{}])[0].get("text", "")
                    else:
                        error_text = await response.text()
                        print(f"[PublisherAgent] MCP tool {tool_name} failed: {response.status} - {error_text}")
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            print(f"[PublisherAgent] Exception calling MCP tool {tool_name}: {e}")
            return f"Exception: {str(e)}"

    async def handle_message_async(self, message):
        print("[PublisherAgent] handle_message_async called with:", message.content)
        try:
            if message.content.type == "text":
                try:
                    claims = json.loads(message.content.text)
                except json.JSONDecodeError as e:
                    return Message(
                        content=TextContent(text=f"Invalid JSON input: {str(e)}"),
                        role=MessageRole.AGENT,
                        parent_message_id=message.message_id,
                        conversation_id=message.conversation_id
                    )

                published_count = 0
                for claim in claims:
                    if "error" in claim:
                        continue
                    try:
                        result = await self.call_mcp_tool(
                            "generate_jekyll_post",
                            statement=claim["statement"],
                            verified=claim["verified"],
                            source=claim["source"]
                        )
                        if "Generated Jekyll post" in result:
                            published_count += 1
                        else:
                            print(f"[PublisherAgent] Unexpected response: {result}")
                    except Exception as e:
                        print(f"[PublisherAgent] MCP call failed for: {claim.get('statement')}\nError: {e}")

                return Message(
                    content=TextContent(text=f"✅ Published {published_count} claims to Jekyll."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            # Fallback message
            return Message(
                content=TextContent(text="Please send a list of claims with 'statement', 'verified', and 'source'."),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

        except Exception as e:
            return Message(
                content=TextContent(text=f"[PublisherAgent Error] {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

# Boot up the Publisher Agent
if __name__ == "__main__":
    agent = PublisherAgent()
    run_server(agent, host=agent.config.get("host", "0.0.0.0"), port=agent.config.get("port", 5004))
