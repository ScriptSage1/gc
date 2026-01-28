import streamlit as st
import os
from datetime import datetime
import pytz
import time

from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI


GOOGLE_API_KEY = "your api key" 
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

st.set_page_config(
    page_title="College RAG Bot",
    layout="wide",
    initial_sidebar_state="collapsed"
)


@st.cache_resource
def initialize_rag():
    def metadata_func(record: dict, metadata: dict) -> dict:
        metadata["article"] = record.get("article") 
        metadata["title"] = record.get("title") 
        return metadata

    loader = JSONLoader(
        file_path="constitution_of_india.json",
        jq_schema=".[]",
        content_key="description",  # remember to change this accoring to the key-value pair later
        metadata_func=metadata_func
    )
    docs = loader.load()

  
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    splits = splitter.split_documents(docs)


    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001") # seems to be a really low rate limit on this, look for alternatives later

    dbdir = "./chroma_db"
    if os.path.exists(dbdir):
        db = Chroma(persist_directory=dbdir, embedding_function=embeddings)
    else:
        db = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=dbdir)
    
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff",
        retriever=db.as_retriever(),
        return_source_documents=True
    )
    return qa_chain

qa = initialize_rag()


def show_greeting():
    if 'greeting_shown' not in st.session_state:
        st.session_state.greeting_shown = False
        st.session_state.show_greeting = True
    
    if st.session_state.show_greeting:
        ist = pytz.timezone('Asia/Kolkata')
        hour = datetime.now(ist).hour
        
        greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if 12 <= hour < 17 else "Good Evening"
        
        placeholder = st.empty()
        placeholder.markdown(f"""
            <div class="greeting-overlay">
                <h1>{greeting}!</h1>
            </div>
            <style>
                .greeting-overlay {{
                    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background: linear-gradient(135deg, #cfd9df 0%, #4f6d8c 100%);
                    padding: 40px 60px; border-radius: 20px; z-index: 9999;
                    animation: fadeIn 0.5s; text-align: center; color: white;
                }}
                @keyframes fadeIn {{ from {{ opacity: 0; scale: 0.8; }} to {{ opacity: 1; scale: 1; }} }}
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2)
        placeholder.empty()
        st.session_state.show_greeting = False
        st.session_state.greeting_shown = True

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');
    .college-name { font-family: 'Playfair Display', serif; font-size: 2.2rem; text-align: center; color: #c5d7e8; border-bottom: 3px solid #4A90E2; padding-bottom: 15px; }
    .catchy-line { font-family: 'Inter', sans-serif; font-size: 1.2rem; text-align: center; color: #f0f2f5; margin: 20px 0 40px 0; font-style: italic; opacity: 0.8; }
    [data-testid="stSidebar"] { background-color: #010203; }
    .chat-history-item { background-color: #262730; padding: 12px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #4A90E2; }
    .main-chat { max-width: 800px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

show_greeting()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("Chat History")
    for chat in st.session_state.chat_history:
        st.markdown(f"<div class='chat-history-item'>{chat['preview']}<br><small>{chat['timestamp']}</small></div>", unsafe_allow_html=True)
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()

st.markdown("<div class='college-name'>GEETHANJALI COLLEGE OF ENGINEERING AND TECHNOLOGY</div>", unsafe_allow_html=True)
st.markdown("<div class='catchy-line'>Because reading the handbook is a tedious job.</div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about the college..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        with st.status("Consulting college records...", expanded=True) as status:
            result = qa.invoke(prompt)
            status.update(label="Information retrieved!", state="complete", expanded=False)
        
        full_response = result["result"]
        
        if result.get("source_documents"):
            sources = set([doc.metadata.get("article") for doc in result["source_documents"] if doc.metadata.get("article")])
            if sources:
                full_response += "\n\n**Sources:** " + ", ".join(sources)
        
        st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.chat_history.insert(0, {
        "preview": prompt[:40] + "..." if len(prompt) > 40 else prompt,
        "timestamp": datetime.now().strftime("%H:%M")
    })