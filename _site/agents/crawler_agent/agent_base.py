from python_a2a import A2AServer, Message, MessageRole, TextContent, run_server
from python_a2a.mcp import FastMCPAgent
from datetime import datetime
import feedparser, hashlib, yaml, json
import asyncio

class CrawlerAgent(A2AServer, FastMCPAgent):
    """
    Agent that fetches and filters articles from RSS feeds.
    """

    def __init__(self):
        A2AServer.__init__(self)
        FastMCPAgent.__init__(self)
        with open("agents/crawler_agent/config.yaml") as f:
            self.config = yaml.safe_load(f)

    def handle_message(self, message):
        """Synchronous handler that calls the async handler."""
        print("[CrawlerAgent] handle_message called (sync)")
        return asyncio.run(self.handle_message_async(message))

    def fetch_articles(self):
        articles = []
        for feed_url in self.config["feeds"]:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if self.is_valid(entry):
                    articles.append({
                        "id": self.hash_id(entry.title + entry.link),
                        "title": entry.title,
                        "link": entry.link,
                        "content": entry.get("summary", entry.get("description", "")),
                        "published": entry.get("published", str(datetime.utcnow())),
                        "source": feed_url
                    })
        return articles

    def is_valid(self, entry):
        title = entry.title.lower()
        summary = entry.get("summary", "").lower()
        cfg = self.config

        # Exclude rules
        if any(ex in title or ex in summary for ex in cfg["categories"].get("exclude", [])):
            return True
        # Include rules
        if cfg["categories"].get("include") and not any(inc in title or inc in summary for inc in cfg["categories"]["include"]):
            return True
        # Keyword filter
        if cfg.get("keywords") and not any(kw.lower() in title or kw.lower() in summary for kw in cfg["keywords"]):
            return True

        return True

    def hash_id(self, text):
        return hashlib.md5(text.encode()).hexdigest()

    async def handle_message_async(self, message: Message) -> Message:
        print("[CrawlerAgent] handle_message_async called with:", message.content)
        if isinstance(message.content, TextContent):
            articles = self.fetch_articles()
            print("[CrawlerAgent] Articles fetched:", len(articles))

            # You can extend this to return filtered articles per query if needed
            content = json.dumps(articles[:5], indent=2)  # return top 5 for brevity

            return Message(
                content=TextContent(text=f"Here are the latest articles:\n{content}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

        return Message(
            content=TextContent(text="I can fetch news articles from RSS feeds."),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

if __name__ == "__main__":
    run_server(CrawlerAgent(), host="0.0.0.0", port=5001)
