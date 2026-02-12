import os
from langchain_groq import ChatGroq

# Initialize LLM (Ensure your API key is in environment variables)
llm = ChatGroq(model="llama-3.1-8b-instant")

def analyzer_node(state):
    """
    Synthesizes tool outputs into a concise industrial recommendation.
    """
    
    # 1. Define the System Message (Fixes the NameError)
    system_msg = (
        "You are the Industrial Strategy Analyzer. "
        "CRITICAL: Be extremely concise. Use bullet points only. "
        "Summarize the findings from the tools provided in the message history. "
        "Do not mention JSON, function names, or internal technical details. "
        "Provide a final 'Proceed' or 'Hold' status based on risk."
    )
    
    # 2. Invoke the LLM with the system context and existing message history
    # We combine the system message with the state messages to give the AI context
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    # 3. Return the update to the graph state
    return {"messages": [response]}