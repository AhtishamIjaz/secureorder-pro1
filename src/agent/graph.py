from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes.researcher import researcher_node
from .nodes.analyzer import analyzer_node
from .tools import fetch_order_status, search_inventory, audit_order_security

def router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "analyzer"

def create_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("tools", ToolNode([fetch_order_status, search_inventory, audit_order_security]))

    workflow.add_edge(START, "researcher")
    workflow.add_conditional_edges("researcher", router, {"tools": "tools", "analyzer": "analyzer"})
    workflow.add_edge("tools", "researcher")
    workflow.add_edge("analyzer", END)

    return workflow.compile(checkpointer=MemorySaver())