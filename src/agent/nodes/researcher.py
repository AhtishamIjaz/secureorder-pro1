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
        "You are the Lead Researcher. You MUST call tools using the exact XML format provided by the interface.\n\n"
        "SYNTAX RULE: Always ensure there is a closing bracket '>' after the function name and before the JSON payload.\n"
        "CORRECT: <function=tool_name>{\"arg\": \"val\"}</function>\n"
        "INCORRECT: <function=tool_name{\"arg\": \"val\"}</function>\n\n"
        "MATH RULE: Calculate all numbers before sending them to a tool. No math strings like '5*10'.\n\n"
        "Now, gather the data for the following request:"
    )
    
    # Process the messages with the safety-first system prompt
    response = llm_with_tools.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    
    return {"messages": [response]}