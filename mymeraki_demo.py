import streamlit as st
import openai
import time
from datetime import datetime

# Configure OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# Inject WhatsApp-style CSS with inline-block bubbles
st.markdown("""
    <style>
    .user-bubble {
        display: inline-block;
        background-color: #DCF8C6;
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-align: left;
    }
    .bot-bubble {
        display: inline-block;
        background-color: #F1F0F0;
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# Display centered company logo
st.markdown("<div style='text-align: center; padding-bottom: 10px;'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Add a demo notice
st.markdown("""
<div style="background-color: #fff8dc; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 15px;">
    <strong>Note:</strong> This is just a basic demo layout to test the knowledge and query handling capabilities of the Meraki AI bot. The final layout will not look like this.
</div>
""", unsafe_allow_html=True)

# Initialize session state for threads and messages
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []

# Callback to handle sending a message
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
    st.session_state.input = ""

# Input field with on_change callback
st.text_input(
    label="",
    placeholder="Type your message here...",
    key="input",
    on_change=send_message,
    label_visibility="collapsed"
)

# Display chat history with adjusted bubble widths
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)


