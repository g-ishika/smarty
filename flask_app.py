"""
flask_app_fast.py - SMARTY with Progress Indicator
"""

from flask import Flask, render_template_string, request, jsonify, Response
from smarty import Assistant, Config
import sys
from pathlib import Path
import traceback
import os
import time
import json
from werkzeug.utils import secure_filename

sys.path.insert(0, str(Path(__file__).parent))

app = Flask(__name__)
app.secret_key = 'smarty-secret-key-2024'

UPLOAD_FOLDER = 'knowledge_base'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'html', 'json', 'csv', 'md', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# SIMPLE HTML WITH LOADING INDICATOR
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMARTY</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #f0f2f5; height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: #ffffff; border-radius: 16px; box-shadow: 0 8px 40px rgba(0, 0, 0, 0.08); width: 100%; max-width: 1000px; height: 90vh; display: flex; flex-direction: column; overflow: hidden; }
        .header { background: #ffffff; border-bottom: 1px solid #e8eaed; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; flex-wrap: wrap; gap: 10px; }
        .header .logo { font-size: 22px; font-weight: 600; color: #1a1a2e; }
        .header .logo span { color: #e91e63; }
        .header .badge { font-size: 12px; padding: 4px 12px; border-radius: 20px; background: #e8f5e9; color: #2e7d32; }
        .header .badge.uploading { background: #e3f2fd; color: #0d47a1; animation: pulse 1s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .header .file-count { font-size: 12px; color: #6b7280; background: #f3f4f6; padding: 4px 12px; border-radius: 20px; }
        .clear-btn { background: none; border: 1px solid #d1d5db; color: #6b7280; padding: 6px 16px; border-radius: 20px; cursor: pointer; font-size: 13px; }
        .clear-btn:hover { background: #f3f4f6; }
        .chat-area { flex: 1; overflow-y: auto; padding: 20px 24px; background: #fafafa; }
        .message { margin-bottom: 16px; max-width: 85%; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .message.user { margin-left: auto; }
        .message .bubble { padding: 12px 18px; border-radius: 12px; word-wrap: break-word; line-height: 1.6; font-size: 14px; white-space: pre-wrap; }
        .message.user .bubble { background: #e91e63; color: #ffffff; border-bottom-right-radius: 4px; }
        .message.assistant .bubble { background: #ffffff; color: #1a1a2e; border: 1px solid #e8eaed; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); }
        .message .bubble .sources { font-size: 12px; color: #6b7280; margin-top: 8px; padding-top: 8px; border-top: 1px solid #e8eaed; }
        .message .bubble .confidence { font-size: 12px; color: #e91e63; margin-top: 4px; }
        .typing-indicator { display: none; padding: 12px 18px; background: #ffffff; border: 1px solid #e8eaed; border-radius: 12px; max-width: 80px; margin-bottom: 16px; }
        .typing-indicator.active { display: block; }
        .typing-dots { display: flex; gap: 4px; }
        .typing-dots span { width: 8px; height: 8px; background: #d1d5db; border-radius: 50%; animation: typing 1.4s infinite; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }
        .input-area { padding: 16px 24px 20px; background: #ffffff; border-top: 1px solid #e8eaed; flex-shrink: 0; }
        .input-row { display: flex; gap: 10px; align-items: flex-end; }
        .input-wrapper { flex: 1; display: flex; gap: 8px; background: #f3f4f6; border-radius: 24px; padding: 4px 4px 4px 16px; border: 1px solid transparent; transition: all 0.2s; }
        .input-wrapper:focus-within { border-color: #e91e63; background: #ffffff; }
        .input-wrapper input { flex: 1; border: none; background: transparent; padding: 10px 0; font-size: 14px; outline: none; color: #1a1a2e; font-family: inherit; }
        .input-wrapper input::placeholder { color: #9ca3af; }
        .input-wrapper input:disabled { opacity: 0.6; }
        .file-btn { background: none; border: none; color: #6b7280; cursor: pointer; padding: 8px 12px; font-size: 18px; border-radius: 50%; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
        .file-btn:hover { background: #e8eaed; color: #e91e63; }
        .file-btn:disabled { opacity: 0.4; }
        .send-btn { background: #e91e63; color: #ffffff; border: none; padding: 10px 24px; border-radius: 24px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; font-family: inherit; }
        .send-btn:hover { background: #c2185b; transform: scale(1.02); }
        .send-btn:disabled { background: #d1d5db; cursor: not-allowed; }
        .file-preview { display: none; align-items: center; gap: 10px; padding: 6px 12px; background: #f3f4f6; border-radius: 20px; margin-top: 8px; font-size: 13px; color: #1a1a2e; }
        .file-preview.show { display: flex; }
        .file-preview .remove-file { background: none; border: none; color: #6b7280; cursor: pointer; font-size: 16px; }
        .file-preview .remove-file:hover { color: #e91e63; }
        .welcome { text-align: center; color: #6b7280; padding: 40px 20px; }
        .welcome h2 { font-size: 20px; font-weight: 500; color: #1a1a2e; margin-bottom: 8px; }
        .welcome p { font-size: 14px; line-height: 1.6; }
        #fileInput { display: none; }
        .status-box { padding: 10px 16px; border-radius: 8px; margin-bottom: 10px; font-size: 13px; display: none; }
        .status-box.show { display: block; }
        .status-box.loading { background: #e3f2fd; color: #0d47a1; }
        .status-box.done { background: #e8f5e9; color: #2e7d32; }
        .status-box.error { background: #ffebee; color: #c62828; }
        .chat-area::-webkit-scrollbar { width: 6px; }
        .chat-area::-webkit-scrollbar-track { background: transparent; }
        .chat-area::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
        @media (max-width: 640px) { body { padding: 10px; } .container { height: 95vh; } .header { padding: 14px 18px; } .chat-area { padding: 14px 16px; } .input-area { padding: 12px 16px 16px; } .input-wrapper { padding-left: 12px; } .send-btn { padding: 8px 16px; font-size: 13px; } .message { max-width: 95%; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SMARTY<span>.</span></div>
            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                <span class="badge" id="statusBadge">Active</span>
                <span class="file-count" id="fileCount"> 0 files</span>
                <button class="clear-btn" onclick="clearChat()">Clear</button>
            </div>
        </div>
        <div class="chat-area" id="chatArea">
            <div class="welcome" id="welcomeMessage">
                <h2>Welcome to SMARTY</h2>
                <p>Upload documents and ask questions</p>
            </div>
            <div class="status-box" id="statusBox"></div>
            <div id="messagesContainer"></div>
            <div class="typing-indicator" id="typingIndicator"><div class="typing-dots"><span></span><span></span><span></span></div></div>
        </div>
        <div class="input-area">
            <div class="file-preview" id="filePreview"><span id="fileName"></span><button class="remove-file" onclick="removeFile()">×</button></div>
            <div class="input-row">
                <div class="input-wrapper">
                    <input type="text" id="questionInput" placeholder="Ask a question or upload a document..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="file-btn" onclick="document.getElementById('fileInput').click()" title="Upload">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 16V4M8 8l4-4 4 4"/><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"/></svg>
                    </button>
                    <input type="file" id="fileInput" multiple accept=".pdf,.docx,.doc,.txt,.html,.json,.csv,.md" onchange="uploadFiles(this.files)">
                </div>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>
    <script>
        let isProcessing = false;
        let isUploading = false;
        
        function showStatus(message, type) {
            const box = document.getElementById('statusBox');
            box.textContent = message;
            box.className = 'status-box show ' + type;
        }
        
        function hideStatus() {
            document.getElementById('statusBox').className = 'status-box';
        }
        
        async function uploadFiles(files) {
            if (isUploading || !files.length) return;
            
            isUploading = true;
            const input = document.getElementById('questionInput');
            const sendBtn = document.getElementById('sendBtn');
            const fileBtn = document.querySelector('.file-btn');
            const badge = document.getElementById('statusBadge');
            
            input.disabled = true;
            sendBtn.disabled = true;
            fileBtn.disabled = true;
            badge.textContent = 'Uploading...';
            badge.className = 'badge uploading';
            
            showStatus('Uploading ' + files.length + ' file(s)...', 'loading');
            
            const formData = new FormData();
            for (let f of files) formData.append('files', f);
            
            try {
                const response = await fetch('/upload', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.success) {
                    showStatus( data.message, 'done');
                    document.getElementById('fileCount').textContent =  data.total_files + ' files';
                    addMessage('assistant', ' Upload complete! ' + data.files_uploaded + ' file(s) added.');
                } else {
                    showStatus( data.error, 'error');
                }
            } catch (error) {
                showStatus( error.message, 'error');
            }
            
            isUploading = false;
            input.disabled = false;
            sendBtn.disabled = false;
            fileBtn.disabled = false;
            badge.textContent = 'Active';
            badge.className = 'badge';
            document.getElementById('fileInput').value = '';
            input.focus();
            
            setTimeout(hideStatus, 5000);
        }
        
        async function sendMessage() {
            if (isProcessing || isUploading) return;
            
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            if (!question) return;
            
            addMessage('user', question);
            input.value = '';
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            document.getElementById('typingIndicator').classList.add('active');
            
            try {
                const formData = new FormData();
                formData.append('question', question);
                const response = await fetch('/ask', { method: 'POST', body: formData });
                const data = await response.json();
                document.getElementById('typingIndicator').classList.remove('active');
                
                let html = data.response;
                if (data.sources && data.sources.length) {
                    html += '<div class="sources">Sources: ' + data.sources.join(', ') + '</div>';
                }
                if (data.confidence) {
                    html += '<div class="confidence">Confidence: ' + (data.confidence * 100).toFixed(1) + '%</div>';
                }
                addMessage('assistant', html);
            } catch (error) {
                document.getElementById('typingIndicator').classList.remove('active');
                addMessage('assistant', 'Error: ' + error.message);
            }
            isProcessing = false;
            document.getElementById('sendBtn').disabled = false;
        }
        
        function addMessage(type, content) {
            document.getElementById('welcomeMessage').style.display = 'none';
            const container = document.getElementById('messagesContainer');
            const div = document.createElement('div');
            div.className = 'message ' + type;
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = content.replace(/\\n/g, '<br>');
            div.appendChild(bubble);
            container.appendChild(div);
            document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;
        }
        
        function clearChat() {
            document.getElementById('messagesContainer').innerHTML = '';
            document.getElementById('welcomeMessage').style.display = 'block';
        }
        
        function removeFile() {
            document.getElementById('filePreview').classList.remove('show');
        }
        
        async function updateFileCount() {
            try {
                const r = await fetch('/status');
                const d = await r.json();
                document.getElementById('fileCount').textContent = d.documents + ' files';
            } catch(e) {}
        }
        
        updateFileCount();
        setInterval(updateFileCount, 30000);
        document.getElementById('questionInput').focus();
    </script>
</body>
</html>
'''

# Initialize
print("=" * 60)
print("SMARTY - Fast Version")
print("=" * 60)

assistant = None
try:
    assistant = Assistant(Config())
    status = assistant.status()
    print(f"Loaded: {status['documents']} docs, {status['vectors']} vectors")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

@app.route('/')
def home():
    return HTML

@app.route('/upload', methods=['POST'])
def upload_files():
    global assistant
    try:
        files = request.files.getlist('files')
        uploaded = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = Path(UPLOAD_FOLDER) / filename
                
                counter = 1
                while filepath.exists():
                    name, ext = os.path.splitext(filename)
                    filepath = Path(UPLOAD_FOLDER) / f"{name}_{counter}{ext}"
                    counter += 1
                
                file.save(filepath)
                uploaded.append(filepath.name)
        
        if uploaded and assistant:
            result = assistant.ingest()
            status = assistant.status()
            return jsonify({
                'success': True,
                'files_uploaded': len(uploaded),
                'total_files': status['documents'],
                'total_chunks': status['vectors'],
                'message': f'Uploaded {len(uploaded)} files. {status["documents"]} docs, {status["vectors"]} chunks'
            })
        
        return jsonify({'success': True, 'files_uploaded': len(uploaded)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ask', methods=['POST'])
def ask():
    if not assistant:
        return jsonify({'response': 'Assistant not loaded'})
    
    question = request.form.get('question', '')
    if not question:
        return jsonify({'response': 'Please ask a question.'})
    
    try:
        response = assistant.ask(question)
        return jsonify({
            'response': response['response'],
            'sources': response.get('sources', []),
            'confidence': response.get('confidence', 0)
        })
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

@app.route('/status')
def status():
    if assistant:
        data = assistant.status()
        return jsonify(data)
    return jsonify({'documents': 0, 'vectors': 0})

if __name__ == '__main__':
    print("=" * 60)
    print(" http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)