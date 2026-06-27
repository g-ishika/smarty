import logging
from pathlib import Path
from typing import Dict, Any, Optional
from smarty.config import Config
from smarty.ingestor import Ingestor
from smarty.chunker import Chunker
from smarty.vector_store import VectorStore
from smarty.generator import Generator

logger = logging.getLogger(__name__)

class Assistant:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.ingestor = Ingestor(self.config)
        self.chunker = Chunker(self.config.chunk_size, self.config.chunk_overlap)
        self.vector_store = VectorStore(self.config)
        self.generator = Generator(self.config)
        self.history = []
        if Path(self.config.vector_index).exists():
            self.vector_store.load()
    
    def ingest(self, directory: str = None) -> Dict[str, Any]:
        directory = directory or self.config.docs_dir
        docs = self.ingestor.load(directory)
        if not docs:
            return {'success': False, 'error': 'No documents found'}
        all_chunks = []
        for file_path, text in docs.items():
            chunks = self.chunker.chunk(text)
            for chunk in chunks:
                all_chunks.append({'text': chunk, 'metadata': {'source': file_path}})
        if not all_chunks:
            return {'success': False, 'error': 'No chunks generated'}
        self.vector_store.add(all_chunks)
        return {'success': True, 'documents': len(docs), 'chunks': len(all_chunks), 'vectors': self.vector_store.count()}
    
    def ask(self, query: str, use_history: bool = True) -> Dict[str, Any]:
        if not query.strip():
            return {'response': 'Please ask a valid question.', 'confidence': 0}
        context = self.vector_store.search(query)
        response = self.generator.generate(query, context)
        self.history.append((query, response['response']))
        if len(self.history) > self.config.history_size:
            self.history.pop(0)
        return response
    
    def clear(self):
        self.history = []
    
    def reset(self):
        self.vector_store.clear()
        self.history = []
    
    def status(self) -> Dict[str, Any]:
        return {'vectors': self.vector_store.count(), 'documents': self.vector_store.doc_count(), 'history': len(self.history), 'model': self.config.embedding_model, 'llm': self.config.llm_model, 'device': self.config.device}
