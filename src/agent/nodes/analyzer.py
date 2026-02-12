from langchain_groq import ChatGroq

def analyzer_node(state):
    """
    The Analyzer node synthesizes the raw tool data into a final 
    business recommendation for the user.
    """
    # Updated to the latest Llama 3.3 model
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
    
    system_msg = (
        "You are the Industrial Strategy Analyzer. "
        "You will receive raw data from tools (weather, prices, inventory). "
        "Your job is to provide a clear, concise summary and a recommendation. "
        "Always highlight any risks, such as high material prices or shipping delays."
    )
    
    # The last message in state is usually the tool output
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}