import os
from dotenv import load_dotenv
from src.agent.graph import create_agent

load_dotenv()

def main():
    app = create_agent()
    print("--- 🛡️ SecureOrder-Pro System (Local Tools) ---")

    user_msg = input("User: ")
    import uuid
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    inputs = {"messages": [{"role": "user", "content": user_msg}]}

    for output in app.stream(inputs, config):
        for node, data in output.items():
            print(f"\n[Node: {node}]")
            if isinstance(data, dict) and "messages" in data:
                m = data["messages"][-1]
                text = getattr(m, "content", None) if m is not None else None
                if text is None and isinstance(m, dict):
                    text = m.get("content")
                print(text)

if __name__ == "__main__":
    main()