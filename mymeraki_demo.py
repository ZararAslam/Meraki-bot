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

# Persistent logo using fixed position
st.markdown("""
    <style>
    .meraki-logo-fixed {
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        background-color: white;
        padding: 10px;
    }
    .chat-input-container {
        position: fixed;
        bottom: 20px;
        left: 0;
        right: 0;
        text-align: center;
        z-index: 1000;
    }
    .chat-input-box input {
        width: 60%;
        padding: 12px 20px;
        border-radius: 25px;
        border: 1px solid #ccc;
        font-size: 16px;
        background-color: #fceeea;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='meraki-logo-fixed'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div><br><br><br><br>", unsafe_allow_html=True)

# Init session variables
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []
if "input" not in st.session_state:
    st.session_state.input = ""

# Display messages ABOVE input
chat_placeholder = st.container()

# Show existing messages first
with chat_placeholder:
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

# Custom input field at the bottom
st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
user_input = st.text_input(
    label="",
    value=st.session_state.input,
    placeholder="Type your message here...",
    key="input_box",
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# Handle message submission via Enter key
if user_input and user_input != st.session_state.input:
    st.session_state.input = user_input
    timestamp_now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp_now
    })

    # Clear input
    st.session_state.input = ""

    # Refresh chat immediately after user sends message
    chat_placeholder.empty()
    with chat_placeholder:
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

    # Send user message to OpenAI
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

