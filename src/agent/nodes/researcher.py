from langchain_groq import ChatGroq
from src.agent.tools import tools # Ensure this list is exported in tools.py

def researcher_node(state):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0).bind_tools(tools)
    
    system_msg = (
        "You are the Lead Researcher. Your primary goal is to gather RAW DATA.\n"
        "1. When you use a tool, you MUST clearly state the result in the conversation.\n"
        "2. If you find a price or weather condition, do not just say 'I found it', say 'The price is X'.\n"
        "3. You are part of an industrial pipeline; accuracy is more important than speed."
    )
    
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    return {"messages": [response]}