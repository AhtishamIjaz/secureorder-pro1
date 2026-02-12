import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from ..state import AgentState
from ..tools import fetch_order_status, search_inventory, audit_order_security

load_dotenv()

def researcher_node(state: AgentState):
    llm = ChatGroq(
        model="llama-3.1-8b-instant", 
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # INDUSTRIAL LOGIC: Strict constraints to prevent "tool hallucination"
    system_msg = {
        "role": "system",
        "content": (
            "You are a Senior Industrial Researcher.\n"
            "1. Use ONLY the provided tools: fetch_order_status, search_inventory, audit_order_security.\n"
            "2. DO NOT attempt to call any other functions like 'analyze_data'.\n"
            "3. If you have the information from a tool, simply provide your response as text.\n"
            "4. NEVER invent tool names."
        )
    }
    
    tools = [fetch_order_status, search_inventory, audit_order_security]
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke([system_msg] + state["messages"])
    return {"messages": [response]}