import streamlit as st
import openai
import time
from datetime import datetime

# Configure OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_55Y5vz9URwhOKhGNszdZjW6c"

# Page setup
st.set_page_config(page_title="MyMeraki AI Chat", layout="wide", page_icon="💬")

# CSS: sticky header/footer, chat bubbles, spacing
st.markdown("""
<style>
.fixed-header {
  position: fixed; top: 0; width: 100%; background: white; z-index: 999;
  text-align: center; padding: 10px 0; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.fixed-footer {
  position: fixed; bottom: 0; width: 100%; background: white; z-index: 999;
  text-align: center; padding: 12px 0; box-shadow: 0 -1px 2px rgba(0,0,0,0.1);
}
.spacer-top { margin-top: 100px; }
.spacer-bottom { margin-bottom: 100px; }
.chat-bubble {
  display: inline-block; padding: 10px 14px; margin: 4px;
  border-radius: 18px; max-width: 75%; font-family: sans-serif;
  position: relative;
}
.chat-bubble .timestamp {
  font-size: 10px; color: #888; text-align: right; margin-top: 4px;
}
.chat-input input {
  width: 60%; padding: 10px 16px; border-radius: 25px;
  border: 1px solid #ccc; font-size: 16px; background: #fceeea;
}
</style>
""", unsafe_allow_html=True)

# Header (logo)
st.markdown("<div class='fixed-header'>", unsafe_allow_html=True)
st.image("meraki-logo.png", width=180)
st.markdown("</div>", unsafe_allow_html=True)
# Push chat below header
st.markdown("<div class='spacer-top'></div>", unsafe_allow_html=True)

# Initialize session state
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.messages = []

# Display chat messages
def show_messages():
    for msg in st.session_state.messages:
        align = "right" if msg["role"] == "user" else "left"
        color = "#fceeea" if msg["role"] == "user" else "#f5f5f5"
        ts = msg.get("timestamp", datetime.now().strftime("%H:%M"))
        st.markdown(f"""
        <div style='text-align: {align}; padding: 4px;'>
          <div class='chat-bubble' style='background:{color};'>
            <div>{msg['content']}</div>
            <div class='timestamp'>{ts}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

show_messages()
# Spacer so last message isn't hidden
st.markdown("<div class='spacer-bottom'></div>", unsafe_allow_html=True)

# Input at bottom: use value="" to auto-clear
st.markdown("<div class='fixed-footer'><div class='chat-input'>", unsafe_allow_html=True)
user_input = st.text_input(
    label="",
    placeholder="Type your message here...",
    value="",  # Always clear after rerun
    key="chat_input",
    label_visibility="collapsed"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# On enter: send
if user_input and user_input.strip():
    ts = datetime.now().strftime("%H:%M")
    # append user message
    st.session_state.messages.append({"role":"user","content":user_input,"timestamp":ts})
    # send to OpenAI
    openai.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=user_input)
    run = openai.beta.threads.runs.create(thread_id=st.session_state.thread_id, assistant_id=ASSISTANT_ID)
    with st.spinner("Typing..."):
        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
            if status.status == "completed": break
            time.sleep(1)
    resp = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    text = resp.data[0].content[0].text.value
    st.session_state.messages.append({"role":"assistant","content":text,"timestamp":datetime.now().strftime("%H:%M")})
  
