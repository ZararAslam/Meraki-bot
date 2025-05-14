import streamlit as st
import openai
import time

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

# Input field without title or label
user_input = st.text_input(
    label="",
    placeholder="Type your message here...",
    key="input",
    label_visibility="collapsed"
)

# Handle user input and fetch assistant response
if user_input and user_input.strip():
    # Append user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Clear the input box instantly
    st.session_state["input"] = ""

    # Send to OpenAI
    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID
    )

    # Wait for completion
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        time.sleep(1)

    # Retrieve assistant reply and append
    messages = openai.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )
    last_message = messages.data[0].content[0].text.value
    st.session_state.messages.append({"role": "assistant", "content": last_message})

# Display all messages
for msg in st.session_state.messages:
    role = "🧑" if msg["role"] == "user" else "🤖"
    st.write(f"{role}: {msg['content']}")
for msg in st.session_state.messages:
    role = "🧑" if msg["role"] == "user" else "🤖"
    st.write(f"{role}: {msg['content']}")



