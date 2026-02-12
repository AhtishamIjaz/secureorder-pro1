from langchain_groq import ChatGroq

def analyzer_node(state):
    """
    Industrial Strategy Analyzer: Synthesizes data into business insights.
    """
    # Updated to Llama 3.3 70B
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
    
    system_msg = (
        "You are the Industrial Strategy Analyzer. "
        "You will receive raw data collected by the researcher (weather, prices, inventory).\n\n"
        "Your job is to:\n"
        "1. Summarize the findings clearly.\n"
        "2. Provide a professional business recommendation.\n"
        "3. Explicitly mention if Karachi weather or high material costs pose a risk.\n"
        "Use a professional, grounded, and decisive tone."
    )
    
    # Analyze the full conversation history
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}