import streamlit as st
import openai
import time
import markdown2
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="MyMeraki Customer Support AI",
    page_icon="💎",
    layout="wide"
)

# Configure OpenAI
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    ASSISTANT_ID = st.secrets.get("ASSISTANT_ID", "asst_55Y5vz9URwhOKhGNszdZjW6c")
except Exception as e:
    st.error("Please configure OPENAI_API_KEY in your Streamlit secrets.")
    st.stop()

# Enhanced WhatsApp-style CSS with MyMeraki branding
st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    section[data-testid="stSidebar"] {display: none;}
    
    /* Remove any top spacing/padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: none;
    }
    
    /* Chat container styling */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #FAFAFA, #F5F5F5);
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #E8E8E8;
    }
    
    /* Message bubbles */
    .message-container {
        margin: 10px 0;
        width: 100%;
        clear: both;
    }
    
    .user-container {
        text-align: right;
    }
    
    .bot-container {
        text-align: left;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #D4AF37, #B8860B);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        min-width: 50px;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(212,175,55,0.4);
        font-size: 14px;
        line-height: 1.4;
        display: inline-block;
        text-align: left;
        white-space: pre-wrap;
        vertical-align: top;
        margin: 0;
    }
    
    /* Remove extra spacing from user bubble content */
    .user-bubble * {
        margin: 0;
        padding: 0;
    }
    
    .user-bubble *:last-child {
        margin-bottom: 0;
    }
    
    .bot-bubble {
        background: linear-gradient(135deg, #FAFAFA, #F5F5F5);
        color: #2C2C2C;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        min-width: 50px;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-size: 14px;
        line-height: 1.4;
        border: 1px solid #E8E8E8;
        display: inline-block;
        text-align: left;
        white-space: pre-wrap;
        vertical-align: top;
    }
    
    /* Completely reset all spacing in bot bubbles */
    .bot-bubble * {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
    }
    
    .bot-bubble h1, .bot-bubble h2, .bot-bubble h3 {
        color: #B8860B !important;
        margin-bottom: 4px !important;
    }
    
    .bot-bubble ul, .bot-bubble ol {
        padding-left: 20px !important;
        margin: 4px 0 !important;
    }
    
    .bot-bubble li {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .bot-bubble code {
        background-color: #F8F6F0 !important;
        padding: 2px 4px !important;
        border-radius: 4px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 13px !important;
        color: #B8860B !important;
    }
    
    .bot-bubble pre {
        background-color: #FAFAFA !important;
        padding: 8px !important;
        border-radius: 6px !important;
        border-left: 4px solid #D4AF37 !important;
        overflow-x: auto !important;
        margin: 4px 0 !important;
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 11px;
        color: #666;
        margin: 2px 8px;
        opacity: 0.7;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #E8E8E8;
        padding: 12px 20px;
        font-size: 14px;
        background-color: #FAFAFA;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D4AF37;
        box-shadow: 0 0 0 0.2rem rgba(212, 175, 55, 0.25);
    }
    
    /* Spinner styling */
    .stSpinner > div {
        text-align: center;
        color: #D4AF37;
    }
    
    /* Demo notice styling */
    .demo-notice {
        background: linear-gradient(135deg, #FDF8E7, #F9F1D7);
        border: 1px solid #D4AF37;
        border-radius: 12px;
        padding: 16px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .demo-notice strong {
        color: #B8860B;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        justify-content: flex-start;
        margin: 10px 0;
    }
    
    .typing-bubble {
        background-color: #F0F0F0;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        color: #666;
        font-style: italic;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* Scrollable chat area */
    .chat-messages {
        max-height: 60vh;
        overflow-y: auto;
        padding-right: 10px;
        margin-bottom: 20px;
        scroll-behavior: smooth;
    }
    
    /* Smoother scrolling for entire page */
    html {
        scroll-behavior: smooth;
    }
    
    body {
        scroll-behavior: smooth;
    }
    
    /* Custom scrollbar */
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: #D4AF37;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: #B8860B;
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "thread_id" not in st.session_state:
    try:
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.session_state.messages = []
        st.session_state.is_processing = False
    except Exception as e:
        st.error(f"Failed to create OpenAI thread: {str(e)}")
        st.stop()

# Function to get assistant response
def get_assistant_response(user_message):
    try:
        # Add user message to thread
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_message
        )
        
        # Create and run the assistant
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Wait for completion with timeout
        timeout = 60  # 60 seconds timeout
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise Exception("Request timed out")
                
            status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            
            if status.status == "completed":
                break
            elif status.status == "failed":
                raise Exception("Assistant run failed")
            elif status.status == "expired":
                raise Exception("Assistant run expired")
                
            time.sleep(1)
        
        # Get the latest message
        messages = openai.beta.threads.messages.list(
            thread_id=st.session_state.thread_id,
            limit=1
        )
        
        if messages.data:
            return messages.data[0].content[0].text.value
        else:
            raise Exception("No response received")
            
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Function to send message
def send_message():
    user_input = st.session_state.user_input.strip()
    if not user_input or st.session_state.is_processing:
        return
    
    # Add user message to chat
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Set processing state
    st.session_state.is_processing = True
    st.session_state.user_input = ""
    
    # Get assistant response
    assistant_response = get_assistant_response(user_input)
    
    # Add assistant response to chat
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "assistant", 
        "content": assistant_response,
        "timestamp": timestamp
    })
    
    # Reset processing state
    st.session_state.is_processing = False

# Header with logo
st.markdown('<div style="text-align: center; margin-bottom: 30px;">', unsafe_allow_html=True)
try:
    st.image("meraki-logo.png", width=200)
except:
    st.markdown("### 🏢 MyMeraki Customer Support AI")
st.markdown("</div>", unsafe_allow_html=True)

# Chat messages container
with st.container():
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # Display chat history
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="message-container user-container">
                    <div>
                        <div class="user-bubble">{msg['content']}</div>
                        <div class="timestamp" style="text-align: right;">{msg.get('timestamp', '')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Use plain text for bot messages too, just like user messages
            st.markdown(f"""
                <div class="message-container bot-container">
                    <div>
                        <div class="bot-bubble">{msg['content']}</div>
                        <div class="timestamp">{msg.get('timestamp', '')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Show typing indicator when processing
    if st.session_state.is_processing:
        st.markdown("""
            <div class="typing-indicator">
                <div class="typing-bubble">
                    Customer Support AI is typing...
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Input section
st.markdown("---")

# Single column for input without send button
st.text_input(
    label="Message",
    placeholder="Ask me anything about MyMeraki services..." + (" (Processing...)" if st.session_state.is_processing else ""),
    key="user_input",
    on_change=send_message,
    label_visibility="collapsed",
    disabled=st.session_state.is_processing
)

# Demo notice
st.markdown("""
<div class="demo-notice">
    <strong>📝 Note:</strong> This is a demo of MyMeraki Customer Support AI backend capabilities. 
    The final frontend will have a more polished design. For specific product information or custom features, 
    please contact us at <strong>hello@altorix.co.uk</strong>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
    Powered by ALTORIX
</div>
""", unsafe_allow_html=True)

# Auto-scroll to bottom (JavaScript injection)
if st.session_state.messages:
    st.markdown("""
        <script>
        setTimeout(function() {
            var chatMessages = document.querySelector('.chat-messages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, 100);
        </script>
    """, unsafe_allow_html=True)
