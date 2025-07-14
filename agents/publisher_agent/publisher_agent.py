from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server, A2AClient
from python_a2a.mcp import FastMCPAgent
import yaml
import json

class PublisherAgent(A2AServer, FastMCPAgent):
    """Agent that publishes verified facts to a Jekyll blog using MCP."""

    def __init__(self):
        # Load config from file
        with open("agents/publisher_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

        mcp_host = self.config.get("mcp_host", "localhost")
        mcp_port = self.config.get("mcp_port", 8000)
        mcp_url = f"http://{mcp_host}:{mcp_port}"

        # Initialize both parents
        A2AServer.__init__(self)
        FastMCPAgent.__init__(self, mcp_servers={"publish": mcp_url})

    async def handle_message_async(self, message):
        """Handles incoming message and publishes claims using MCP."""
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
                            "publish",
                            "generate_jekyll_post",
                            statement=claim["statement"],
                            verified=claim["verified"],
                            source=claim["source"]
                        )
                        if isinstance(result, int) and result == 0:
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
