import os
from langchain_groq import ChatGroq
from ..state import AgentState

def analyzer_node(state: AgentState):
    llm = ChatGroq(
        model="llama-3.1-70b-versatile", # Using a larger model for better reasoning
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    system_msg = {
        "role": "system",
        "content": (
            "You are a Strategic Manufacturing Consultant.\n"
            "Your job is to take the raw data provided by the Researcher and create an Executive Summary.\n\n"
            "STRUCTURE YOUR RESPONSE:\n"
            "1. STATUS OVERVIEW: Briefly state what was found.\n"
            "2. IMPACT ANALYSIS: How do the current prices or weather affect our production?\n"
            "3. ACTION PLAN: Provide 2-3 clear steps (e.g., 'Buy now while prices are low' or 'Inform the client of a 2-day weather delay').\n"
            "Keep your tone professional, concise, and data-driven."
        )
    }
    
    # The Analyzer looks at the entire conversation, including the tool outputs
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}