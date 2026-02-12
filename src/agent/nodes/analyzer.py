from langchain_groq import ChatGroq

def analyzer_node(state):
    """
    Industrial Strategy Analyzer: Synthesizes data into business insights.
    """
    # Updated to Llama 3.3 70B
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
    
    prompt = (
    "You are a professional industrial analyst. "
    "Use the raw tool data provided to give a final answer. "
    "DO NOT show function names or JSON. "
    "Format: 1-2 Bullet points only. Extremely brief."
)
    # ... existing invoke ...
    
    # Analyze the full conversation history
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}