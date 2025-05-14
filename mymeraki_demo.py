import streamlit as st
import openai
import time
from datetime import datetime

# Configure OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# Display centered company logo
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

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
    # Append user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Call OpenAI
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
    # Append assistant reply
    resp = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    reply = resp.data[0].content[0].text.value
    st.session_state.messages.append({"role": "assistant", "content": reply})
    # Clear input box
    st.session_state.input = ""

# Input field with on_change callback
st.text_input(
    label="",
    placeholder="Type your message here...",
    key="input",
    on_change=send_message,
    label_visibility="collapsed"
)

# Display chat history
for msg in st.session_state.messages:
    prefix = "🧑" if msg["role"] == "user" else "🤖"
    st.write(f"{prefix}: {msg['content']}")


