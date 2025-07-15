from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server, A2AClient
import yaml
import json
import asyncio
import aiohttp

class FactCheckerAgent(A2AServer):
    """Agent that verifies factual claims using MCP Wikidata tool."""

    def __init__(self):
        # Load MCP config
        with open("agents/fact_checker_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

        mcp_host = self.config.get("mcp_host", "localhost")
        mcp_port = self.config.get("mcp_port", 8000)
        self.mcp_url = f"http://{mcp_host}:{mcp_port}"
        print(f"[FactCheckerAgent] Connecting to MCP server at: {self.mcp_url}")

        # Init parent
        A2AServer.__init__(self)

    def handle_message(self, message):
        """Synchronous handler that calls the async handler."""
        print("[FactCheckerAgent] handle_message called (sync)")
        return asyncio.run(self.handle_message_async(message))

    async def call_mcp_tool(self, tool_name, **kwargs):
        """Call MCP tool directly via HTTP."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.mcp_url}/tools/{tool_name}"
                payload = kwargs
                
                print(f"[FactCheckerAgent] Calling MCP tool {tool_name} with payload: {payload}")
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"[FactCheckerAgent] MCP tool {tool_name} result: {result}")
                        return result.get("content", [{}])[0].get("text", "")
                    else:
                        error_text = await response.text()
                        print(f"[FactCheckerAgent] MCP tool {tool_name} failed: {response.status} - {error_text}")
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            print(f"[FactCheckerAgent] Exception calling MCP tool {tool_name}: {e}")
            return f"Exception: {str(e)}"

    async def handle_message_async(self, message):
        print("[FactCheckerAgent] handle_message_async called with:", message.content)
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
                    result = await self.call_mcp_tool("check_wikidata", statement=claim)
                    try:
                        # Parse the JSON response from the MCP tool
                        if isinstance(result, str):
                            result_data = json.loads(result)
                        else:
                            result_data = result
                            
                        if isinstance(result_data, dict) and result_data.get("error"):
                            results.append({
                                "statement": claim,
                                "verified": False,
                                "source": "",
                                "error": result_data["error"]
                            })
                        else:
                            results.append({
                                "statement": claim,
                                "verified": result_data.get("verified", False),
                                "source": result_data.get("source", "")
                            })
                    except (json.JSONDecodeError, AttributeError) as e:
                        results.append({
                            "statement": claim,
                            "verified": False,
                            "source": "",
                            "error": f"Failed to parse result: {str(e)}"
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
