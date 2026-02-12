import streamlit as st
import uuid
import sqlite3
from src.agent.graph import create_agent

# 1. Page Configuration
st.set_page_config(page_title="SecureOrder Pro", page_icon="🛡️", layout="wide")

st.markdown("# 🛡️ **SecureOrder-Pro: Industrial AI**")
st.markdown("### *Professional Audit & Inventory Intelligence*")
st.divider()

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

def get_all_threads():
    try:
        conn = sqlite3.connect("checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = [row[0] for row in cursor.fetchall()]
        conn.close()
        return threads
    except Exception: return []

# 2. Sidebar with Audit Logs
with st.sidebar:
    st.header("📜 Session Manager")
    all_threads = get_all_threads()
    for tid in all_threads:
        if st.button(f"🧵 {tid[:8]}", key=tid):
            st.session_state.thread_id = tid
            config = {"configurable": {"thread_id": tid}}
            state = st.session_state.agent.get_state(config)
            st.session_state.messages = []
            if getattr(state, "values", None) and "messages" in state.values:
                for msg in state.values["messages"]:
                    content = getattr(msg, "content", None) if msg is not None else None
                    if content is None and isinstance(msg, dict):
                        content = msg.get("content")
                        role = msg.get("role", "assistant")
                    else:
                        role = getattr(msg, "role", "assistant")
                    if content:
                        st.session_state.messages.append({"role": role, "content": content})
            st.rerun()

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

# 4. Render
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Execution Logic
if prompt := st.chat_input("System command...", disabled=st.session_state.processing):
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        with st.spinner("⚡ Processing Industrial Logic..."):
            try:
                # Use stream to show the 'Technical Trace' if checkbox is checked
                final_output = None
                for event in st.session_state.agent.stream({"messages": [{"role": "user", "content": prompt}]}, config):
                    if show_trace:
                        for node, data in event.items():
                            st.caption(f"Node: {node} active.")
                    final_output = event

                # Sync UI state from agent memory
                state = st.session_state.agent.get_state(config)
                new_msgs = []
                for m in state.values.get("messages", []):
                    content = getattr(m, "content", None) if m is not None else None
                    if content is None and isinstance(m, dict):
                        content = m.get("content")
                        role = m.get("role", "assistant")
                    else:
                        role = getattr(m, "role", "assistant")
                    if content:
                        new_msgs.append({"role": role, "content": content})

                st.session_state.messages = new_msgs
                if st.session_state.messages:
                    st.markdown(st.session_state.messages[-1]["content"])
                
            except Exception as e:
                st.error(f"Critical System Failure: {str(e)}")
    
    st.session_state.processing = False
    st.rerun()