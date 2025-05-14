import streamlit as st
import openai
import time

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# Page settings
st.set_page_config(page_title="MyMeraki AI Chat", layout="centered")

# Display centered Meraki logo using st.image
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)

# Initialize thread and message history
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []  # Start with no messages

# Chat display in bubbles
chat_placeholder = st.empty()

with chat_placeholder.container():
    for msg in st.session_state.messages:
        align = "right" if msg["role"] == "user" else "left"
        bubble_color = "#fceeea" if msg["role"] == "user" else "#f5f5f5"
        st.markdown(
            f"""
            <div style='text-align: {align}; padding: 4px;'>
                <div style='display: inline-block; background: {bubble_color}; padding: 10px 14px; margin: 4px; border-radius: 18px; max-width: 75%; font-family: sans-serif;'>
                    {msg['content']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Input box at bottom
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...", key="input")
    send_btn = st.form_submit_button("Send")

# Handle input and response
if send_btn and user_input:
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

    with st.spinner("Thinking..."):
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

    # Get latest assistant message
    last_message = messages.data[0].content[0].text.value
    st.session_state.messages.append({"role": "assistant", "content": last_message})

    # Auto-scroll simulation by re-running the app
    st.experimental_rerun()


