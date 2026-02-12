from langchain_groq import ChatGroq
from src.agent.tools import tools # Ensure this list is exported in tools.py

def researcher_node(state):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0).bind_tools(tools)
    
    system_msg = (
        "You are the Industrial Strategy Researcher. "
        "CRITICAL RULE: Be extremely concise. Use bullet points. "
        "Do not repeat the researcher's raw data unless necessary. "
        "Give a 1-sentence summary, a 1-sentence recommendation, and a final 'Proceed/Hold' status."
    )
    
    response = llm.invoke([{"role": "system", "content": system_msg}] + state["messages"])
    return {"messages": [response]}