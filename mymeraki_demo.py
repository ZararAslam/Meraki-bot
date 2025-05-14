import streamlit as st
import openai
import time
from datetime import datetime

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# Page settings
st.set_page_config(
    page_title="MyMeraki AI Chat",
    layout="centered",
    page_icon="💬"
)

# Centered logo
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Init session variables
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []

# Input box (bottom)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...", key="input")
    send_btn = st.form_submit_button("Send")

# Process message
if send_btn and user_input:
    timestamp_now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp_now
    })

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
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(1)

    messages = openai.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    last_message = messages.data[0].content[0].text.value
    timestamp_now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "assistant",
        "content": last_message,
        "timestamp": timestamp_now
    })

# Display messages
chat_placeholder = st.empty()
with chat_placeholder.container():
    for msg in st.session_state.messages:
        align = "right" if msg["role"] == "user" else "left"
        bubble_color = "#fceeea" if msg["role"] == "user" else "#f5f5f5"
        timestamp = msg.get("timestamp", "")
        st.markdown(
            f"""
            <div style='text-align: {align}; padding: 4px;'>
                <div style='display: inline-block; background: {bubble_color}; padding: 10px 14px; margin: 4px; border-radius: 18px; max-width: 75%; font-family: sans-serif;'>
                    <div>{msg['content']}</div>
                    <div style='font-size: 10px; color: #888; text-align: right; margin-top: 4px;'>{timestamp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


