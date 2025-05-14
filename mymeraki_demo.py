import streamlit as st
import openai
import time

openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

st.title("MyMeraki AI Assistant 💬")

if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []

user_input = st.text_input("Type your question here 💡")

if user_input:
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
    st.session_state.messages.append({"role": "assistant", "content": last_message})

for msg in st.session_state.messages:
    role = "🧑" if msg["role"] == "user" else "🤖"
    st.write(f"{role}: {msg['content']}")

