from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes.researcher import researcher_node
from .nodes.analyzer import analyzer_node
from .tools import (
    fetch_order_status, search_inventory, audit_order_security,
    get_material_price, get_shipping_weather, convert_currency
)

def router(state: AgentState):
    last_msg = state["messages"][-1]
    return "tools" if hasattr(last_msg, "tool_calls") and last_msg.tool_calls else "analyzer"

def create_agent():
    workflow = StateGraph(AgentState)
    executable_tools = [fetch_order_status, search_inventory, audit_order_security, 
                        get_material_price, get_shipping_weather, convert_currency]
    
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("tools", ToolNode(executable_tools))

    workflow.add_edge(START, "researcher")
    workflow.add_conditional_edges("researcher", router, {"tools": "tools", "analyzer": "analyzer"})
    workflow.add_edge("tools", "researcher")
    workflow.add_edge("analyzer", END)

    # Professional Change: interrupt_before creates a manual approval gate
    return workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["tools"] 
    )