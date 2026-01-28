import streamlit as st
from datetime import datetime
import pytz
import time


st.set_page_config(
    page_title="College RAG Bot",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def show_greeting():
    if 'greeting_shown' not in st.session_state:
        st.session_state.greeting_shown = False
        st.session_state.show_greeting = True
    
    # Only show greeting on fresh load
    if st.session_state.show_greeting:
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist)
        hour = current_time.hour
        

        if 5 <= hour < 12:
            greeting = "Good Morning"
        elif 12 <= hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        greeting_placeholder = st.empty()

        greeting_placeholder.markdown(f"""
        <div style='
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #cfd9df 0%, #9fb7c9 40%, #4f6d8c 100%);
            padding: 40px 60px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.35);
            z-index: 9999;
            animation: fadeIn 0.5s;
        '>
        <h1 style='
            color: #f8fbff;
            text-align: center;
            font-family: Inter, sans-serif;
            font-size: 3rem;
            margin: 0;
            font-weight: 600;
            text-shadow: 0 2px 8px rgba(0,0,0,0.25);
        '>{greeting}!</h1>
    </div>
    <style>
        @keyframes fadeIn {{
            from {{ 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(0.85); 
                filter: blur(2px);
            }}
            to {{ 
                opacity: 1; 
                transform: translate(-50%, -50%) scale(1); 
                filter: blur(0);
            }}
        }}
    </style>
    """, unsafe_allow_html=True)


        time.sleep(2.5)
        
        greeting_placeholder.empty()

        st.session_state.show_greeting = False
        st.session_state.greeting_shown = True

show_greeting()

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');
    
    /* College name font - Playfair Display (elegant serif) */
    .college-name {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        color: #c5d7e8;
        border-bottom: 3px solid #4A90E2;
        padding-bottom: 15px;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    /* Catchy line font - Inter (modern sans-serif) */
    .catchy-line {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 500;
        text-align: center;
        color: #f0f2f5;
        margin-top: 60px;
        margin-bottom: 40px;
        font-style: italic;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #010203;
    }
    
    .chat-history-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #f0f2f5;
        margin-bottom: 20px;
    }
    
    .chat-history-item {
        background-color: #9ba5b0;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 8px;
        border-left: 4px solid #4A90E2;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .chat-history-item:hover {
        background-color: #e8f4ff;
        transform: translateX(5px);
    }
    
    .chat-preview {
        font-size: 0.9rem;
        color: #333;
        font-weight: 500;
        margin-bottom: 5px;
    }
    
    .chat-timestamp {
        font-size: 0.75rem;
        color: #888;
    }
    
    /* Main chat container */
    .main-chat {
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom button styling */
    .stButton button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton button:hover {
        background-color: #357ABD;
    }
</style>
""", unsafe_allow_html=True)


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"preview": "What are the library timings?", "timestamp": "2 hours ago"},
        {"preview": "Tell me about the CSE department faculty", "timestamp": "Yesterday"},
        {"preview": "Upcoming college events this month?", "timestamp": "2 days ago"},
        {"preview": "Hostel accommodation details", "timestamp": "3 days ago"},
        {"preview": "Exam schedule for this semester", "timestamp": "1 week ago"},
    ]

if 'messages' not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.markdown("<div class='chat-history-title'>Chat History</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"""
        <div class='chat-history-item'>
            <div class='chat-preview'>{chat['preview']}</div>
            <div class='chat-timestamp'>{chat['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("Clear History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


st.markdown("<div class='college-name'>GEETHANJALI COLLEGE OF ENGINEERING AND TECHNOLOGY</div>", unsafe_allow_html=True)


st.markdown("<div class='catchy-line'>Because reading the handbook is a tedious job.</div>", unsafe_allow_html=True)

st.markdown("<div class='main-chat'>", unsafe_allow_html=True)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if prompt := st.chat_input("Ask about college events, faculty, course details, facilities..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        st.write("Searching through college records...")
        st.write("Analyzing relevant documents...")
        st.write("*Response *")
    
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Searching through college records...\n\nAnalyzing relevant documents...\n\nResponse"
    })
    
    
    st.session_state.chat_history.insert(0, {
        "preview": prompt[:50] + "..." if len(prompt) > 50 else prompt,
        "timestamp": "Just now"
    })
    
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
""", unsafe_allow_html=True)

