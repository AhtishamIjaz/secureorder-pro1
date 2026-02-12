import streamlit as st
import uuid
import sqlite3
from src.agent.graph import create_agent
from langchain_core.messages import HumanMessage

# 1. Page Configuration & Styling
st.set_page_config(page_title="SecureOrder Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    .sidebar-history-btn { margin-bottom: 5px; text-align: left; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Logic
def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    # Content stores the message, session_id groups the chat
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (session_id TEXT, role TEXT, content TEXT)''')
    conn.commit()
    return conn

def save_msg(session_id, role, content):
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO messages VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()

def load_msgs(session_id):
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ?", (session_id,))
    return [{"role": r, "content": c} for r, c in c.fetchall()]

def get_all_sessions():
    conn = init_db()
    c = conn.cursor()
    # This gets the first message of every session to use as a "Title"
    c.execute("SELECT DISTINCT session_id FROM messages")
    return [row[0] for row in c.fetchall()]

# 3. Sidebar: The History Archive
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

with st.sidebar:
    st.title("🛡️ Admin Panel")
    
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()
    st.markdown("### 📜 Past Conversations")
    
    # Get all unique past sessions
    sessions = get_all_sessions()
    for s_id in sessions:
        # Create a button for each past session
        # Shortening the ID for the button label
        if st.button(f"Chat: {s_id[:8]}...", key=s_id, use_container_width=True):
            st.session_state.thread_id = s_id
            st.rerun()

# 4. Agent Initialization
if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

# Load current session messages
chat_history = load_msgs(st.session_state.thread_id)

st.title("SecureOrder-Pro: Industrial AI")
st.caption(f"Current Session: {st.session_state.thread_id}")

# Display history
for m in chat_history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 5. Input Logic
if prompt := st.chat_input("Ask about orders or inventory..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    save_msg(st.session_state.thread_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("⚡ Processing..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = st.session_state.agent.invoke(
                {"messages": [HumanMessage(content=prompt)]}, 
                config
            )
            
            final_text = ""
            for msg in reversed(result["messages"]):
                if msg.content and isinstance(msg.content, str):
                    final_text = msg.content
                    break
            
            st.markdown(final_text)
            save_msg(st.session_state.thread_id, "assistant", final_text)
    
    st.rerun()