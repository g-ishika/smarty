```markdown
# SMARTY - Intelligent Document Assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

## Overview

SMARTY is a lightweight, intelligent document assistant designed to help users analyze and query their documents. Built with a Retrieval-Augmented Generation (RAG) approach, it enables seamless interaction with uploaded documents through a clean web interface.

## Features

- Multi-format document support: PDF, DOCX, TXT, MD
- Intelligent keyword-based search and retrieval
- Interactive question-answering interface
- Source attribution for every answer
- Modern, responsive web interface
- Lightweight architecture with minimal dependencies
- Fast document indexing and retrieval

## Architecture

The system follows a modular RAG pipeline:

1. Document Ingestion - Loads and parses documents from various formats
2. Text Chunking - Splits documents into manageable, overlapping chunks
3. Vector Indexing - Stores document chunks with their embeddings for fast retrieval
4. Query Processing - Converts user questions into search queries
5. Retrieval - Finds the most relevant document chunks
6. Response Generation - Constructs answers based on retrieved context

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

Clone the repository:

```
git clone https://github.com/g-ishika/smarty.git
cd smarty
```

Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate
```

On Windows:

```
venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

### Running the Application

#### Web Interface

```
python flask_app.py
```

Navigate to `http://localhost:5000` in your browser.

#### Command Line Interface

```
python run.py
```

## Project Structure

```
smarty/
├── smarty/
│   ├── __init__.py
│   ├── assistant.py
│   ├── config.py
│   ├── ingestor.py
│   ├── chunker.py
│   ├── vector_store.py
│   └── generator.py
├── knowledge_base/
├── data/
├── tests/
├── flask_app.py
├── run.py
├── requirements.txt
└── README.md
```

## Configuration

Edit `smarty/config.py` to customize:

```
chunk_size: int = 1000
chunk_overlap: int = 200
top_k: int = 5
```

## Usage Examples

### Uploading Documents

1. Click the uploading icon in the web interface
2. Select your PDF, DOCX, or TXT files
3. Wait for automatic indexing

### Asking Questions

Question: What are the AML compliance requirements?

Response: Found 5 relevant passages.

From: AML_Regulation.pdf
The Anti-Money Laundering regulations require financial institutions to implement customer due diligence, transaction monitoring, and suspicious activity reporting procedures.

## Dependencies

- Flask - Web framework
- PyPDF2 - PDF parsing
- python-docx - DOCX parsing
- BeautifulSoup4 - HTML parsing

See `requirements.txt` for complete list.

## Development

### Running Tests

```
python -m pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- Built with Flask for web interface
- PDF processing with PyPDF2
- DOCX processing with python-docx

## Contact

Project Link: https://github.com/g-ishika/smarty

---

Made with Python
```
