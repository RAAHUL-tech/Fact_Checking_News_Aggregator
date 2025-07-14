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
        if message.content.type == "text":
            text = message.content.text.strip().lower()
            if text in ["start", "run", "pipeline", "run pipeline"]:
                return self._run_pipeline(message)

        return Message(
            content=TextContent(text="Type `start` to run the fact-checking pipeline."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

    def _run_pipeline(self, message):
        try:
            # Step 1: Crawl news
            crawl_resp = self.crawler.send_message(Message(
                content=TextContent(text="start"),
                role=MessageRole.USER
            ))

            # Step 2: Extract factual claims
            extract_resp = self.extractor.send_message(Message(
                content=TextContent(text=crawl_resp.content.text),
                role=MessageRole.USER
            ))

            # Step 3: Check the claims
            check_resp = self.checker.send_message(Message(
                content=TextContent(text=extract_resp.content.text),
                role=MessageRole.USER
            ))

            # Step 4: Publish the validated results
            publish_resp = self.publisher.send_message(Message(
                content=TextContent(text=check_resp.content.text),
                role=MessageRole.USER
            ))
            print(crawl_resp.content.text)
            print(extract_resp.content.text)
            print(check_resp.content.text)
            print(publish_resp.content.text)


            return Message(
                content=TextContent(
                    text="✅ Pipeline complete:\n\n" + publish_resp.content.text
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
