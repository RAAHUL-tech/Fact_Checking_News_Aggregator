from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server, A2AClient
from python_a2a.mcp import FastMCPAgent
import yaml
import json

class FactCheckerAgent(A2AServer, FastMCPAgent):
    """Agent that verifies factual claims using MCP Wikidata tool."""

    def __init__(self):
        # Load MCP config
        with open("agents/fact_checker_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

        mcp_host = self.config.get("mcp_host", "localhost")
        mcp_port = self.config.get("mcp_port", 8000)
        mcp_url = f"http://{mcp_host}:{mcp_port}"

        # Init both parents
        A2AServer.__init__(self)
        FastMCPAgent.__init__(self, mcp_servers={"factcheck": mcp_url})

    async def handle_message_async(self, message):
        """Handles A2A message to check claims against Wikidata."""
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

                results = []
                for claim in claims:
                    result = await self.call_mcp_tool("factcheck", "check_wikidata", statement=claim)
                    if isinstance(result, dict) and result.get("error"):
                        results.append({
                            "statement": claim,
                            "verified": False,
                            "source": "",
                            "error": result["error"]
                        })
                    else:
                        results.append({
                            "statement": claim,
                            "verified": result.get("verified", False),
                            "source": result.get("source", "")
                        })

                return Message(
                    content=TextContent(text=json.dumps(results, indent=2)),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id
                )

            return Message(
                content=TextContent(text="Please send a JSON array of claims as plain text."),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        except Exception as e:
            return Message(
                content=TextContent(text=f"[FactCheckerAgent Error] {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

# Run the agent server
if __name__ == "__main__":
    agent = FactCheckerAgent()
    run_server(agent, host=agent.config.get("host", "0.0.0.0"), port=agent.config.get("port", 5003))
