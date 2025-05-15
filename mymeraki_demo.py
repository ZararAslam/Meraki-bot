import streamlit as st
import openai
import time
import markdown2  # Converts markdown (like [link](url)) to HTML
from datetime import datetime

# Configure OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# WhatsApp-style CSS with tighter bot-bubble spacing
st.markdown("""
    <style>
    .user-bubble {
        display: inline-block;
        background-color: #DCF8C6;
        color: black;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 4px 0;
        max-width: 80%;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-align: left;
    }
    .bot-bubble {
        display: inline-block;
        background-color: #F1F0F0;
        color: black;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 2px 0;
        max-width: 80%;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# Centered logo
st.markdown("<div style='text-align: center; padding-bottom: 10px;'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Session state for thread and messages
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []

# Send message callback
def send_message():
    user_input = st.session_state.input
    if not user_input:
        return
    st.session_state.messages.append({"role": "user", "content": user_input})
    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID
    )
    with st.spinner("Typing..."):
        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            time.sleep(1)
    resp = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    reply = resp.data[0].content[0].text.value
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.input = ""  # Clear text box

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        html = markdown2.markdown(msg["content"])
        st.markdown(f"<div class='bot-bubble'>{html}</div>", unsafe_allow_html=True)

# Input field
st.text_input(
    label="",
    placeholder="Type your message here...",
    key="input",
    on_change=send_message,
    label_visibility="collapsed"
)

# Demo banner
st.markdown("""
<div style="background-color: #fff8dc; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-top: 15px;">
    <strong>Note:</strong> This is just a basic demo layout to test the technicals, knowledge and query handling capabilities of Meraki AI. The final visual layout will not look like this.
</div>
""", unsafe_allow_html=True)
