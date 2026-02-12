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
    Lead Researcher node: Gathers data and ensures math is calculated 
    before tool injection to avoid Groq Schema errors.
    """
    # Using the updated Llama 3.3 model
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    
    system_msg = (
        "You are the Lead Researcher in an Industrial AI system. "
        "Your goal is to gather all necessary data using tools.\n\n"
        "CRITICAL RULE: Never send a mathematical expression like '88 * 0.5' to a tool. "
        "You must calculate the final number yourself (e.g., 44.0) and pass only "
        "that single number into the tool arguments. Failuer to do this will crash the system.\n\n"
        "TOOL USAGE:\n"
        "- Use 'convert_currency' for all PKR/USD conversions after calculating the total.\n"
        "- Use 'get_material_price' for raw material market data.\n"
        "- Use 'search_inventory' to check stock levels."
    )
    
    # Process the messages with the safety-first system prompt
    response = llm_with_tools.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}