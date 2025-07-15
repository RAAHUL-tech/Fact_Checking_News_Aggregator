from python_a2a import A2AClient, Message, TextContent, MessageRole
import argparse

def interactive_session(client):
    print("\n🧠 FactCheck Pipeline Client")
    print("Type `start` to begin the pipeline, or `exit` to quit.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n> ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            message = Message(
                content=TextContent(text=user_input),
                role=MessageRole.USER
            )

            print("⏳ Sending to orchestrator...")
            response = client.send_message(message)

            print(f"\n🛰️  Orchestrator Response:\n{response.content.text}")

        except Exception as e:
            print(f"❌ Error: {e}\nTry again or type 'exit' to quit.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FactCheck Pipeline Client")
    parser.add_argument("--endpoint", default="http://localhost:5005/a2a",
                        help="Orchestrator endpoint URL")
    args = parser.parse_args()

    client = A2AClient(args.endpoint)
    interactive_session(client)
