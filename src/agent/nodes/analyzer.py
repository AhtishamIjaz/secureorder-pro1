from langchain_groq import ChatGroq

def analyzer_node(state):
    """
    Industrial Strategy Analyzer: Synthesizes data into business insights.
    """
    # Updated to Llama 3.3 70B
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
    
    system_msg = (
        "You are the Industrial Strategy Analyzer. "
        "CRITICAL RULE: Be extremely concise. Use bullet points. "
        "Do not repeat the researcher's raw data unless necessary. "
        "Give a 1-sentence summary, a 1-sentence recommendation, and a final 'Proceed/Hold' status."
    )
    # ... existing invoke ...
    
    # Analyze the full conversation history
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}