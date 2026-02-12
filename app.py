import streamlit as st
import uuid
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

# 4. Helper Function: Safe Message Parsing
def sync_messages_from_state(state_values):
    """Safely converts LangGraph state messages (dict or objects) to UI list."""
    if "messages" not in state_values:
        return []
    
    new_msgs = []
    for m in state_values["messages"]:
        # Handle Dictionary format (common after interrupts)
        if isinstance(m, dict):
            content = m.get("content", "")
            role = "user" if m.get("role") in ["user", "human"] else "assistant"
        # Handle Object format (common during live execution)
        else:
            content = getattr(m, "content", "")
            role = "user" if getattr(m, "type", "") == "human" else "assistant"
        
        if content:
            new_msgs.append({"role": role, "content": content})
    return new_msgs

# 5. Render Conversation History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Execution Logic
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# CHECK FOR INTERRUPTS: Approval Gate
current_state = st.session_state.agent.get_state(config)
if current_state.next:
    st.warning("🚦 **Action Pending:** The AI is requesting permission to use tools.")
    if st.button("✅ Approve & Execute Tool Call"):
        with st.spinner("Executing approved action..."):
            # Resuming the graph by passing None
            for event in st.session_state.agent.stream(None, config, stream_mode="values"):
                if event:
                    st.session_state.messages = sync_messages_from_state(event)
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
                    pass # Values mode updates the state; we sync after loop

                # Sync final state to UI
                final_state = st.session_state.agent.get_state(config)
                st.session_state.messages = sync_messages_from_state(final_state.values)
                
                # Display final answer if not interrupted
                if not final_state.next and st.session_state.messages:
                    st.markdown(st.session_state.messages[-1]["content"])
                
            except Exception as e:
                st.error(f"Critical System Failure: {str(e)}")
    
    st.session_state.processing = False
    st.rerun()