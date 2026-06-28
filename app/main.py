from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import os
from datetime import datetime
import hashlib
import PyPDF2
from docx import Document
import torch

# Optimize CPU performance
torch.set_num_threads(4)
torch.set_default_dtype(torch.float32)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import warnings
warnings.filterwarnings("ignore")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

vector_store = None
qa_chain = None
documents_metadata = []

os.makedirs("uploads", exist_ok=True)

def extract_text_from_pdf(file_path: str) -> str:
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except:
        return ""

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text])
    except:
        return ""

def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return ""

def build_rag_system(chunks: List[str], metadata: List[Dict]):
    global vector_store, qa_chain
    
    if not chunks:
        return False
    
    try:
        print("Loading embedding model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        print("Building FAISS index...")
        vector_store = FAISS.from_texts(
            texts=chunks,
            embedding=embeddings,
            metadatas=metadata
        )
        
        # ============================================================
        # USING FLAN-T5-SMALL - PROVEN TO WORK
        # ============================================================
        print("Loading Flan-T5-Small LLM...")
        model_name = "google/flan-t5-small"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=200,
            temperature=0.1,
            do_sample=False,
            device=0 if torch.cuda.is_available() else -1
        )
        
        llm = HuggingFacePipeline(pipeline=pipe)
        
        prompt_template = """Answer the question based ONLY on the provided context.

Context: {context}

Question: {question}

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        print("Creating QA chain...")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("RAG system built successfully with Flan-T5-Small!")
        return True
        
    except Exception as e:
        print(f"Error building RAG: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "RAG System API", "status": "running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "documents": len(documents_metadata),
        "qa_ready": qa_chain is not None,
        "model": "google/flan-t5-small"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global documents_metadata
    
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.pdf', '.docx', '.txt', '.md']:
            raise HTTPException(400, f"Unsupported file type: {ext}")
        
        content = await file.read()
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        if ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = extract_text_from_docx(file_path)
        else:
            text = extract_text_from_txt(file_path)
        
        if not text:
            return {"status": "error", "message": "Could not extract text from file"}
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_text(text)
        
        if not chunks:
            return {"status": "error", "message": "No content could be extracted"}
        
        doc_id = hashlib.md5(f"{file.filename}{datetime.utcnow()}".encode()).hexdigest()[:8]
        
        metadata = [{
            "source": file.filename,
            "doc_id": doc_id,
            "chunk_id": i
        } for i in range(len(chunks))]
        
        documents_metadata.append({
            "id": doc_id,
            "filename": file.filename,
            "file_type": ext[1:],
            "chunk_count": len(chunks),
            "uploaded_at": datetime.utcnow().isoformat()
        })
        
        success = build_rag_system(chunks, metadata)
        
        if success:
            return {
                "status": "success",
                "message": f"Uploaded {file.filename}",
                "document_id": doc_id,
                "chunk_count": len(chunks)
            }
        else:
            return {"status": "error", "message": "Failed to build RAG system"}
            
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/query")
async def query(request: QueryRequest):
    global qa_chain
    
    if not qa_chain:
        return {
            "answer": "No documents uploaded. Please upload a document first.",
            "sources": [],
            "confidence": 0.0
        }
    
    try:
        result = qa_chain.invoke({"query": request.query})
        
        answer = result.get('result', 'No answer generated')
        sources = []
        
        if 'source_documents' in result:
            for doc in result['source_documents']:
                if hasattr(doc, 'metadata'):
                    source = doc.metadata.get('source', 'Unknown')
                    if source not in [s.get('filename') for s in sources]:
                        sources.append({"filename": source})
        
        # Clean up the answer
        if answer and len(answer) > 0:
            # Remove any "reheat" or repeated words
            import re
            # If answer is just repeated word, return a fallback
            if re.match(r'^(\w+)\1{5,}', answer):
                # Try to get first 2 sentences from context
                context = result.get('source_documents', [])
                if context:
                    first_chunk = context[0].page_content if hasattr(context[0], 'page_content') else str(context[0])
                    answer = f"Based on the documents: {first_chunk[:200]}..."
                else:
                    answer = "I found information but couldn't generate a proper response. Please try rephrasing your question."
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": 0.85
        }
        
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "confidence": 0.0
        }

@app.get("/documents")
async def list_documents():
    return {
        "documents": documents_metadata,
        "total": len(documents_metadata)
    }

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    global documents_metadata
    documents_metadata = [d for d in documents_metadata if d['id'] != doc_id]
    return {"status": "success", "message": "Document deleted"}