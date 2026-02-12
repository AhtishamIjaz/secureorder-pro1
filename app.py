import streamlit as st
import uuid
import sqlite3
from src.agent.graph import create_agent

# 1. Page Configuration
st.set_page_config(page_title="SecureOrder Pro", page_icon="🛡️", layout="wide")

st.markdown("# 🛡️ **SecureOrder-Pro: Industrial AI**")
st.markdown("### *Professional Audit & Inventory Intelligence*")
st.divider()

# Initialize the agent once
if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

# 2. Sidebar with Session Management
with st.sidebar:
    st.header("📜 Session Manager")
    
    if st.button("➕ New Industrial Session", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    show_trace = st.checkbox("Show Technical Trace", value=True)

# 3. State Setup
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# 4. Render Conversation History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Execution Logic
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# CHECK FOR INTERRUPTS: If the agent is paused, show approval button
current_state = st.session_state.agent.get_state(config)
if current_state.next:
    st.warning("🚦 **Action Pending:** The AI is requesting permission to use tools.")
    if st.button("✅ Approve & Execute Tool Call"):
        with st.spinner("Executing approved action..."):
            # Resuming the graph by passing None as input
            for event in st.session_state.agent.stream(None, config, stream_mode="values"):
                if "messages" in event:
                    st.session_state.messages = [
                        {"role": m.type if hasattr(m, 'type') else "assistant", "content": m.content} 
                        for m in event["messages"] if m.content
                    ]
            st.rerun()

# Regular Chat Input
if prompt := st.chat_input("System command...", disabled=st.session_state.processing):
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("⚡ Processing Industrial Logic..."):
            try:
                # Start the stream
                for event in st.session_state.agent.stream(
                    {"messages": [{"role": "user", "content": prompt}]}, 
                    config,
                    stream_mode="values"
                ):
                    if show_trace and "messages" in event:
                        # Optional: Log the last node active
                        pass

                # After streaming, check if we hit an interrupt or finished
                new_state = st.session_state.agent.get_state(config)
                
                # Update UI messages from the Graph State
                if "messages" in new_state.values:
                    final_msgs = []
                    for m in new_state.values["messages"]:
                        role = "user" if m.type == "human" else "assistant"
                        if m.content:
                            final_msgs.append({"role": role, "content": m.content})
                    st.session_state.messages = final_msgs
                
                # If finished, display the last message
                if not new_state.next:
                    st.markdown(st.session_state.messages[-1]["content"])
                
            except Exception as e:
                st.error(f"Critical System Failure: {str(e)}")
    
    st.session_state.processing = False
    st.rerun()