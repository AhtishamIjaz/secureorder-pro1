import streamlit as st
import uuid
import sqlite3
from src.agent.graph import create_agent # Fixed: Matching the function name

# 1. Page Configuration
st.set_page_config(page_title="SecureOrder Pro", page_icon="🛡️", layout="wide")

st.markdown("# 🛡️ **SecureOrder-Pro: Industrial AI**")
st.markdown("### *Professional Audit & Inventory Intelligence*")
st.divider()

# Initialize the agent once
if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

# Helper to see past sessions (only if using a database like SQLite)
def get_all_threads():
    try:
        conn = sqlite3.connect("checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = [row[0] for row in cursor.fetchall()]
        conn.close()
        return threads
    except Exception: return []

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

# 4. Render Conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Execution Logic
if prompt := st.chat_input("System command...", disabled=st.session_state.processing):
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)

    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        with st.spinner("⚡ Processing Industrial Logic..."):
            try:
                # Streaming response to show node transitions
                for event in st.session_state.agent.stream(
                    {"messages": [{"role": "user", "content": prompt}]}, 
                    config
                ):
                    if show_trace:
                        for node in event.keys():
                            st.caption(f"⚙️ Node: `{node}` completed.")

                # Pull the final state to update UI
                state = st.session_state.agent.get_state(config)
                final_msg = state.values["messages"][-1]
                
                # Render the final response
                st.markdown(final_msg.content)
                st.session_state.messages.append({"role": "assistant", "content": final_msg.content})
                
            except Exception as e:
                st.error(f"Critical System Failure: {str(e)}")
    
    st.session_state.processing = False
    st.rerun()