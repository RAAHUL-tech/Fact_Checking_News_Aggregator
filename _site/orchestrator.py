import asyncio
from python_a2a import A2AServer, A2AClient, Message, TextContent, MessageRole, run_server
import os

class FactCheckOrchestrator(A2AServer):
    """Orchestrates crawler → extractor → checker → publisher pipeline."""

    def __init__(self):
        super().__init__()

        # Define clients for the agent chain
        self.crawler = A2AClient("http://localhost:5001/a2a")
        self.extractor = A2AClient("http://localhost:5002/a2a")
        self.checker = A2AClient("http://localhost:5003/a2a")
        self.publisher = A2AClient("http://localhost:5004/a2a")

    def handle_message(self, message):
        """Synchronous handler that calls the async handler."""
        print("[Orchestrator] handle_message called (sync)")
        return asyncio.run(self.handle_message_async(message))

    async def handle_message_async(self, message):
        print("[Orchestrator] handle_message_async called with:", message.content)
        if message.content.type == "text":
            text = message.content.text.strip().lower()
            if text in ["start", "run", "pipeline", "run pipeline"]:
                return await self._run_pipeline(message)

        return Message(
            content=TextContent(text="Type `start` to run the fact-checking pipeline."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

    def _get_text_content(self, msg, label):
        if isinstance(msg.content, TextContent):
            return msg.content.text
        else:
            print(f"[Orchestrator] Warning: {label} response is not TextContent. Got: {type(msg.content)}")
            return f"[Non-text content: {type(msg.content)}]"

    async def _run_pipeline(self, message):
        print("[Orchestrator] _run_pipeline called")
        try:
            # Step 1: Crawl news
            crawl_resp = await self.crawler.send_message_async(Message(
                content=TextContent(text="start"),
                role=MessageRole.USER
            ))
            crawl_text = self._get_text_content(crawl_resp, "Crawler")

            # Step 2: Extract factual claims
            extract_resp = await self.extractor.send_message_async(Message(
                content=TextContent(text=crawl_text),
                role=MessageRole.USER
            ))
            extract_text = self._get_text_content(extract_resp, "Extractor")

            # Step 3: Check the claims
            check_resp = await self.checker.send_message_async(Message(
                content=TextContent(text=extract_text),
                role=MessageRole.USER
            ))
            check_text = self._get_text_content(check_resp, "Checker")

            # Step 4: Publish the validated results
            publish_resp = await self.publisher.send_message_async(Message(
                content=TextContent(text=check_text),
                role=MessageRole.USER
            ))
            publish_text = self._get_text_content(publish_resp, "Publisher")

            print(crawl_text)
            print(extract_text)
            print(check_text)
            print(publish_text)

            return Message(
                content=TextContent(
                    text="✅ Pipeline complete:\n\n" + publish_text
                ),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )
        except Exception as e:
            return Message(
                content=TextContent(text=f"❌ Error in pipeline: {str(e)}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

if __name__ == "__main__":
    run_server(FactCheckOrchestrator(), host="0.0.0.0", port=5005)
