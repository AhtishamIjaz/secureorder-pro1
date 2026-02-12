import streamlit as st
from src.agent.graph import graph_builder
from langgraph.checkpoint.memory import InMemorySaver # New: Memory Import

# --- Page Config ---
st.set_page_config(page_title="SecureOrder-Pro: Industrial AI", layout="wide")
st.title("🏭 SecureOrder-Pro: Industrial AI")
st.subheader("Llama 3.3 70B + Multi-Agent Strategy")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# New: Initialize the Memory Checkpointer in Session State
if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = InMemorySaver()

if "agent" not in st.session_state:
    # Compile the graph with the checkpointer for persistence
    st.session_state.agent = graph_builder.compile(checkpointer=st.session_state.checkpointer)

# --- Chat Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your industrial query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔄 Processing Industrial Logic..."):
            # Configuration for the checkpointer (Memory Bucket)
            # This 'thread_id' keeps the conversation history linked
            config = {"configurable": {"thread_id": "industrial_session_1"}}
            
            # Invoke the agent with history awareness
            try:
                result = st.session_state.agent.invoke(
                    {"messages": st.session_state.messages},
                    config=config
                )
                
                # Get the final response from the last node (Analyzer)
                final_response = result["messages"][-1].content
                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                if "429" in str(e):
                    st.warning("Rate limit hit. Waiting for token bucket to refill...")
                elif "400" in str(e):
                    st.warning("Syntax error in tool call. Checking model formatting...")