"""
RAG System - Document Q&A Interface
Professional, full-featured, no emojis.
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

st.set_page_config(
    page_title="Document Q&A System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - Full styling
st.markdown("""
<style>
    /* Reset and base */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Chat container */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        border: 1px solid #e5e7eb;
    }
    
    /* User messages */
    .stChatMessage[data-testid="user"] {
        background-color: #e8f0fe;
        border-color: #c5d8f0;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="assistant"] {
        background-color: #ffffff;
        border-color: #e5e7eb;
    }
    
    /* Input area */
    .stChatInput {
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 4px 8px;
    }
    
    .stChatInput:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
    }
    
    /* File upload area in sidebar */
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        color: #6b7280;
        transition: all 0.2s;
    }
    
    .upload-area:hover {
        border-color: #6366f1;
        background-color: #f8fafc;
    }
    
    /* Document list */
    .doc-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #f3f4f6;
        font-size: 13px;
    }
    
    .doc-name {
        color: #111827;
        font-weight: 500;
    }
    
    .doc-type {
        color: #6b7280;
        font-size: 11px;
        background: #f3f4f6;
        padding: 2px 8px;
        border-radius: 4px;
    }
    
    .doc-size {
        color: #9ca3af;
        font-size: 11px;
    }
    
    /* Confidence badges */
    .confidence-high {
        color: #22c55e;
        font-weight: 600;
        background: #f0fdf4;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
    }
    
    .confidence-medium {
        color: #eab308;
        font-weight: 600;
        background: #fefce8;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
    }
    
    .confidence-low {
        color: #ef4444;
        font-weight: 600;
        background: #fef2f2;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
    }
    
    /* Metadata cards */
    .metadata-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 8px 0;
    }
    
    .metadata-item {
        background: #f8fafc;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
    }
    
    .metadata-label {
        font-size: 11px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metadata-value {
        font-size: 14px;
        font-weight: 600;
        color: #111827;
        margin-top: 2px;
    }
    
    /* Source citations */
    .source-item {
        background: #f8fafc;
        padding: 6px 12px;
        border-radius: 4px;
        margin: 4px 0;
        border-left: 3px solid #6366f1;
        font-size: 13px;
    }
    
    /* Header */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 16px;
    }
    
    .app-title {
        font-size: 22px;
        font-weight: 600;
        color: #111827;
    }
    
    .app-subtitle {
        font-size: 13px;
        color: #6b7280;
        font-weight: 400;
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-online {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-online::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #22c55e;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-offline {
        background: #fef2f2;
        color: #991b1b;
    }
    
    .status-offline::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #ef4444;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #6b7280;
    }
    
    .empty-state h3 {
        color: #111827;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    /* Toast notifications */
    .toast {
        padding: 10px 16px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 14px;
    }
    
    .toast-success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
    }
    
    .toast-error {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
    }
    
    /* Footer */
    .app-footer {
        border-top: 1px solid #e5e7eb;
        padding: 12px 0;
        margin-top: 16px;
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #9ca3af;
    }
    
    /* Scrollbar */
    .stChatMessage::-webkit-scrollbar {
        width: 4px;
    }
    
    .stChatMessage::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = "http://localhost:8000"
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'upload_toast' not in st.session_state:
    st.session_state.upload_toast = None
if 'document_list' not in st.session_state:
    st.session_state.document_list = []


def send_query(query: str) -> Optional[Dict[str, Any]]:
    """Send query to backend API."""
    try:
        response = requests.post(
            f"{st.session_state.backend_url}/query",
            json={
                "query": query,
                "top_k": 5,
                "search_type": "similarity",
                "include_reranking": True,
                "include_guardrails": True
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def upload_file(file) -> Optional[Dict[str, Any]]:
    """Upload file to backend."""
    try:
        files = {"file": file}
        response = requests.post(
            f"{st.session_state.backend_url}/upload",
            files=files,
            params={"chunk_strategy": "recursive"},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_documents() -> List[Dict[str, Any]]:
    """Get list of documents."""
    try:
        response = requests.get(
            f"{st.session_state.backend_url}/documents",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('documents', [])
        return []
    except:
        return []


def check_backend_status() -> Dict[str, Any]:
    """Check backend health."""
    try:
        response = requests.get(
            f"{st.session_state.backend_url}/health",
            timeout=5
        )
        if response.status_code == 200:
            return {"status": "online", "data": response.json()}
        return {"status": "offline"}
    except:
        return {"status": "offline"}


# Get backend status
status = check_backend_status()

# ============================================================================
# HEADER
# ============================================================================
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("""
    <div>
        <span class="app-title">Document Q&A</span>
        <span class="app-subtitle">Retrieval Augmented Generation</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if status["status"] == "online":
        st.markdown('<span class="status-badge status-online">Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-offline">Offline</span>', unsafe_allow_html=True)

with col3:
    # Document count
    doc_count = len(get_documents())
    st.markdown(f'<div style="text-align:right;font-size:13px;color:#6b7280;">Documents: {doc_count}</div>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# SIDEBAR - Document Management
# ============================================================================
with st.sidebar:
    st.markdown("### Document Management")
    st.divider()
    
    # File upload
    st.markdown("#### Upload Files")
    uploaded_files = st.file_uploader(
        "Select files",
        type=['pdf', 'docx', 'txt', 'md'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    result = upload_file(uploaded_file)
                    if result and result.get('status') == 'success':
                        st.session_state.uploaded_files.append(uploaded_file.name)
                        st.success(f"Loaded: {uploaded_file.name}")
                        st.session_state.document_list = get_documents()
                    else:
                        st.error(f"Failed: {uploaded_file.name}")
    
    st.divider()
    
    # Document list
    st.markdown("#### Documents")
    docs = get_documents()
    if docs:
        for doc in docs:
            filename = doc.get('filename', 'Unknown')
            file_type = doc.get('file_type', 'unknown')
            size = doc.get('size', 0)
            size_str = f"{size / 1024:.1f}KB" if size > 0 else ""
            
            st.markdown(f"""
            <div class="doc-item">
                <span class="doc-name">{filename}</span>
                <span class="doc-type">{file_type}</span>
                <span class="doc-size">{size_str}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No documents uploaded")
    
    st.divider()
    st.caption(f"Version 1.0.0 · {datetime.now().strftime('%Y-%m-%d')}")

# ============================================================================
# CHAT INTERFACE
# ============================================================================

# Chat container
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="empty-state">
            <h3>Ask questions about your documents</h3>
            <p>Upload documents in the sidebar and start querying</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show metadata for assistant messages
                if message["role"] == "assistant" and "metadata" in message:
                    meta = message["metadata"]
                    
                    # Confidence badge
                    confidence = meta.get('confidence', 0)
                    if confidence > 0.7:
                        badge = f'<span class="confidence-high">{confidence:.1%}</span>'
                    elif confidence > 0.4:
                        badge = f'<span class="confidence-medium">{confidence:.1%}</span>'
                    else:
                        badge = f'<span class="confidence-low">{confidence:.1%}</span>'
                    
                    # Sources
                    sources = meta.get('sources', [])
                    
                    with st.expander("Details", expanded=False):
                        # Metadata grid
                        st.markdown(f"""
                        <div class="metadata-grid">
                            <div class="metadata-item">
                                <div class="metadata-label">Confidence</div>
                                <div class="metadata-value">{badge}</div>
                            </div>
                            <div class="metadata-item">
                                <div class="metadata-label">Sources</div>
                                <div class="metadata-value">{len(sources)}</div>
                            </div>
                            <div class="metadata-item">
                                <div class="metadata-label">Response Time</div>
                                <div class="metadata-value">{meta.get('total_time', 0):.2f}s</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Sources list
                        if sources:
                            st.markdown("**Source Documents**")
                            for source in sources:
                                st.markdown(f"""
                                <div class="source-item">
                                    {source.get('filename', 'Unknown')}
                                    <span style="color:#6b7280;font-size:11px;margin-left:8px;">
                                        {source.get('file_type', '')}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)

# ============================================================================
# INPUT AREA
# ============================================================================

# Chat input at bottom
prompt = st.chat_input("Ask a question about your documents...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            result = send_query(prompt)
        
        if result:
            answer = result.get('answer', 'No answer generated')
            metadata = result.get('metadata', {})
            metadata['sources'] = result.get('sources', [])
            metadata['confidence'] = result.get('confidence', 0)
            
            st.markdown(answer)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "metadata": metadata
            })
        else:
            error_msg = "Unable to process query. Please check the system status."
            st.markdown(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "metadata": {}
            })
    
    st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Document Q&A System v1.0.0")
with col2:
    st.caption("Powered by LangChain · FAISS · HuggingFace")
with col3:
    st.caption(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")