import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from ..state import AgentState
# 1. Import the new tools
from ..tools import (
    fetch_order_status, 
    search_inventory, 
    audit_order_security,
    get_material_price,     # Added
    get_shipping_weather,   # Added
    convert_currency        # Added
)

load_dotenv()

def researcher_node(state: AgentState):
    llm = ChatGroq(
        model="llama-3.1-8b-instant", 
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Updated Industrial Logic to include new capabilities
    system_msg = {
        "role": "system",
        "content": (
            "You are a Senior Industrial Researcher with real-time data access.\n"
            "1. Use ONLY these tools: fetch_order_status, search_inventory, audit_order_security, "
            "get_material_price, get_shipping_weather, convert_currency.\n"
            "2. If inventory is low, check the live market price using 'get_material_price'.\n"
            "3. If an order is delayed, check the city's weather via 'get_shipping_weather'.\n"
            "4. For international clients, use 'convert_currency' for accuracy.\n"
            "5. Provide raw facts to the Analyzer; do not make final business decisions yourself."
        )
    }
    
    # 2. Add new tools to the binding list
    tools = [
        fetch_order_status, 
        search_inventory, 
        audit_order_security,
        get_material_price,
        get_shipping_weather,
        convert_currency
    ]
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke([system_msg] + state["messages"])
    return {"messages": [response]}