"""Debug helper: inspect the agent object returned by `create_agent()`.

Run from project root:

    python debug_agent.py

Paste the output here.
"""

from src.agent.graph import create_agent
import os
import pprint


def main():
    print("Environment: GROQ_API_KEY set? ->", bool(os.getenv("GROQ_API_KEY")))
    try:
        agent = create_agent()
    except Exception as e:
        print("Error creating agent:", repr(e))
        return

    print("Agent type:", type(agent))
    attrs = [a for a in dir(agent) if not a.startswith("_")]
    print("Visible attributes/methods:")
    pprint.pprint(attrs)

    checks = ["stream", "invoke", "get_state", "run", "start", "compile", "send"]
    for name in checks:
        print(f"Has {name}:", hasattr(agent, name))

    # If get_state is present, show a short repr of its doc or callable
    if hasattr(agent, "get_state"):
        try:
            gs = agent.get_state
            print("get_state callable repr:", repr(gs))
        except Exception as e:
            print("Error inspecting get_state:", e)


if __name__ == "__main__":
    main()
