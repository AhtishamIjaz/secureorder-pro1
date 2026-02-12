import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from ..state import AgentState

load_dotenv()

def analyzer_node(state: AgentState):
    llm = ChatGroq(
        model="llama-3.1-8b-instant", 
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    system_prompt = (
        "You are the Final Reviewer. Summarize tool findings into a professional "
        "industrial report using Markdown tables."
    )
    
    messages = [("system", system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}