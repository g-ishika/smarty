# README.md

```markdown
# Document Q&A System

A production-ready Retrieval Augmented Generation (RAG) system for querying documents using state-of-the-art language models. Upload PDFs, DOCX, TXT, or Markdown files and ask questions about their content.

## Features

- Document upload and text extraction (PDF, DOCX, TXT, MD)
- Semantic search using FAISS vector database
- Context-aware responses using Flan-T5 language model
- Source attribution for generated answers
- RESTful API with Swagger documentation
- Streamlit web interface
- Docker support for containerized deployment

## Architecture

The system consists of three main components:

1. **Document Processing Pipeline**: Extracts and chunks text from uploaded documents
2. **Vector Store**: FAISS index with sentence transformer embeddings for semantic retrieval
3. **Language Model**: Flan-T5-small for generating answers based on retrieved context

```
User Query → Embedding → FAISS Search → Context Retrieval → LLM Generation → Response
```

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Streamlit
- **Vector Database**: FAISS
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Language Model**: Google Flan-T5-small
- **Orchestration**: LangChain
- **Containerization**: Docker

## Prerequisites

- Python 3.11 or higher
- pip
- (Optional) Docker and Docker Compose

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <https://github.com/g-ishika/smarty/tree/main>
cd rag-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the required directories:
```bash
mkdir -p uploads data
```

### Docker Deployment

```bash
docker-compose up -d --build
```

## Running the Application

### Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at: http://localhost:8000/docs

### Start the Frontend Interface

Open a new terminal and run:

```bash
streamlit run frontend/streamlit_app.py --server.port=8501
```

Access the web interface at: http://localhost:8501

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Root endpoint |
| GET | /health | Health check |
| POST | /upload | Upload a document |
| POST | /query | Submit a question |
| GET | /documents | List uploaded documents |
| DELETE | /documents/{doc_id} | Delete a document |

### Example API Usage

**Upload a Document:**
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/upload
```

**Query the System:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}' \
  http://localhost:8000/query
```

## Configuration

Create a `.env` file in the project root with the following options:

```env
# Application
APP_NAME=RAG-System
APP_ENV=development
DEBUG=True

# Backend
BACKEND_URL=http://localhost:8000

# Model Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=google/flan-t5-small
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=3
MAX_NEW_TOKENS=200
TEMPERATURE=0.1
```

## Project Structure

```
rag-system/
├── app/
│   └── main.py              # FastAPI application
├── frontend/
│   └── streamlit_app.py     # Streamlit web interface
├── uploads/                 # Uploaded document storage
├── data/                    # Vector index storage
├── requirements.txt         # Python dependencies
├── Dockerfile               # Backend container definition
├── docker-compose.yml       # Multi-container orchestration
├── .env.example             # Environment variables template
└── README.md                # Documentation
```

## Performance Considerations

- First query after document upload may be slower as models load into memory
- Processing time depends on document size and CPU performance
- Recommended for documents up to 100 pages for optimal performance
- The system runs entirely on CPU; GPU support is available with minor modifications

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Upload fails**: Check that the `uploads/` directory exists and is writable

3. **Slow responses**: Consider reducing `TOP_K` or `MAX_NEW_TOKENS` in configuration

4. **Memory issues**: Use `flan-t5-small` instead of larger models

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## Contact

Email- ishikagupta2595@gmail.com
