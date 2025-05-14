import streamlit as st
import openai
import time
from datetime import datetime

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# Page settings
st.set_page_config(page_title="MyMeraki AI Chat", layout="wide", page_icon="💬")

# CSS for sticky header, chat bubbles, and footer
st.markdown("""
    <style>
    .fixed-header {
        position: fixed;
        top: 0;
        width: 100%;
        background: white;
        z-index: 999;
        text-align: center;
        padding: 10px 0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    .fixed-footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: white;
        z-index: 999;
        text-align: center;
        padding: 12px 0;
        box-shadow: 0 -1px 2px rgba(0, 0, 0, 0.1);
    }
    .chat-input input {
        width: 60%;
        padding: 10px 16px;
        border-radius: 25px;
        border: 1px solid #ccc;
        font-size: 16px;
        background: #fceeea;
    }
    .spacer-top {
        margin-top: 100px;
    }
    .spacer-bottom {
        margin-bottom: 100px;
    }
    </style>
""", unsafe_allow_html=True)

# Sticky header with Meraki logo
st.markdown("<div class='fixed-header'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Add spacing to prevent overlap with fixed elements
st.markdown("<div class='spacer-top'></div>", unsafe_allow_html=True)

# Session state setup
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Chat display
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        align = "right" if msg["role"] == "user" else "left"
        bubble_color = "#fceeea" if msg["role"] == "user" else "#f5f5f5"
        timestamp = msg.get("timestamp", datetime.now().strftime("%H:%M"))
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

# Add bottom spacer to avoid input overlap
st.markdown("<div class='spacer-bottom'></div>", unsafe_allow_html=True)

# Fixed input footer
st.markdown("<div class='fixed-footer'><div class='chat-input'>", unsafe_allow_html=True)
user_input = st.text_input(
    label="",
    value=st.session_state.input_text,
    placeholder="Type your message here...",
    key="input_text",
    label_visibility="collapsed"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# On message submission
if user_input and user_input.strip():
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    st.session_state["input_text"] = ""

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
    st.session_state.messages.append({
        "role": "assistant",
        "content": last_message,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    st.experimental_rerun()
