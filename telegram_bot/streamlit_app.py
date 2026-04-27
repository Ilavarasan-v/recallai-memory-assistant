import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from memory_engine import build_context_prompt, clear_memory, get_memory_summary, save_episode

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# Use a fixed user ID for Streamlit testing
STREAMLIT_USER_ID = 99999

# ── Groq Integration ──────────────────────────────────────────────────────────
def ask_groq(user_message: str, context_prompt: str = "") -> str:
    """Send a message to Groq with optional episodic memory context."""
    system_instruction = (
        "You are a helpful personal AI assistant. "
        "You have a memory of past conversations with this user. "
        "Use that memory to give personalised, context-aware replies. "
        "Remember the user's name, preferences, goals, interests, problems - you remember it. "
        "Keep responses concise. Use plain text, no markdown."
    )
    full_system = (
        system_instruction + "\n\n" + context_prompt
        if context_prompt
        else system_instruction
    )
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ── Streamlit UI ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="🤖 AI Chat Bot", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .memory-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        color: #ccc;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 AI Chat Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Personal assistant with episodic memory · Powered by Groq</div>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🧠 View Memory", use_container_width=True):
        summary = get_memory_summary(STREAMLIT_USER_ID)
        st.info(summary)
    if st.button("🗑️ Clear Memory", use_container_width=True):
        clear_memory(STREAMLIT_USER_ID)
        st.session_state.messages = []
        st.success("Memory cleared! Fresh start.")
    st.divider()
    st.caption("This is a local test interface. Your Telegram bot uses the same memory engine.")

# Initialize chat history in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type a message..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            context_prompt = build_context_prompt(STREAMLIT_USER_ID, query=prompt)
            response = ask_groq(prompt, context_prompt)
            st.write(response)

    # Save to memory + session
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_episode(STREAMLIT_USER_ID, prompt, response)