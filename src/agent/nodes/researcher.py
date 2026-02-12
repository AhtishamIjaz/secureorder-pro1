from langchain_groq import ChatGroq
from src.agent.tools import (
    fetch_order_status, 
    search_inventory, 
    audit_order_security,
    get_material_price,
    get_shipping_weather,
    convert_currency
)

# List of tools available to the researcher
tools = [
    fetch_order_status, 
    search_inventory, 
    audit_order_security,
    get_material_price,
    get_shipping_weather,
    convert_currency
]

def researcher_node(state):
    """
    The Researcher node uses the 70B model to decide which tools to use 
    based on the user's complex industrial query.
    """
    # Updated to the latest Llama 3.3 model
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    
    system_msg = (
        "You are the Lead Researcher in an Industrial AI system. "
        "Your goal is to gather all necessary data using the provided tools. "
        "If the user asks about money, ALWAYS use the 'convert_currency' tool. "
        "If they ask about raw materials, use 'get_material_price'."
    )
    
    # Process the messages
    response = llm_with_tools.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}