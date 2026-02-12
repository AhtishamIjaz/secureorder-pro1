from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes.researcher import researcher_node
from .nodes.analyzer import analyzer_node
from .tools import (
    fetch_order_status, 
    search_inventory, 
    audit_order_security,
    get_material_price,
    get_shipping_weather,
    convert_currency
)

def router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "analyzer"

def create_agent():
    workflow = StateGraph(AgentState)
    
    executable_tools = [
        fetch_order_status, 
        search_inventory, 
        audit_order_security,
        get_material_price, 
        get_shipping_weather, 
        convert_currency
    ]
    
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("tools", ToolNode(executable_tools))

    workflow.add_edge(START, "researcher")
    workflow.add_conditional_edges("researcher", router, {"tools": "tools", "analyzer": "analyzer"})
    workflow.add_edge("tools", "researcher")
    workflow.add_edge("analyzer", END)

    # We use MemorySaver() here for short-term persistence
    return workflow.compile(checkpointer=MemorySaver())