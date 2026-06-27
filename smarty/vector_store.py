"""
vector_store.py - ULTRA FAST (Keyword Search Only)
"""

import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


class VectorStore:
    """FAST keyword-based search (no embeddings)"""
    
    def __init__(self, config):
        self.config = config
        self.metadata = []
        self.texts = []
        self.word_index = defaultdict(list)
    
    def add(self, chunks: List[Dict[str, Any]]) -> None:
        """Add chunks to search index"""
        if not chunks:
            return
        
        for chunk in chunks:
            text = chunk['text']
            metadata = chunk.get('metadata', {})
            
            # Store text
            idx = len(self.texts)
            self.texts.append(text)
            metadata['text'] = text
            metadata['id'] = idx
            self.metadata.append(metadata)
            
            # Index words (fast)
            words = re.findall(r'\w+', text.lower())
            for word in set(words):  # Use set to avoid duplicates
                self.word_index[word].append(idx)
        
        self.save()
        logger.info(f"Added {len(chunks)} chunks. Indexed {len(self.word_index)} unique words")
    
    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Keyword search - INSTANT"""
        if not self.texts:
            return []
        
        k = k or self.config.top_k
        k = min(k, len(self.texts))
        
        # Get query words
        query_words = re.findall(r'\w+', query.lower())
        if not query_words:
            return []
        
        # Score each document
        scores = defaultdict(float)
        
        for word in query_words:
            for idx in self.word_index.get(word, []):
                scores[idx] += 1
        
        # Sort by score
        sorted_indices = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:k]
        
        results = []
        for idx in sorted_indices:
            results.append({
                'score': scores[idx] / max(len(query_words), 1),
                'text': self.texts[idx],
                'source': self.metadata[idx].get('source', 'unknown'),
                'metadata': self.metadata[idx]
            })
        
        return results
    
    def count(self) -> int:
        return len(self.texts)
    
    def doc_count(self) -> int:
        sources = set()
        for meta in self.metadata:
            if 'source' in meta:
                sources.add(meta['source'])
        return len(sources)
    
    def save(self):
        try:
            Path(self.config.data_dir).mkdir(exist_ok=True)
            with open(self.config.metadata_file, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'texts': self.texts,
                    'word_index': dict(self.word_index)
                }, f)
            logger.info(f"Saved index: {len(self.texts)} chunks")
        except Exception as e:
            logger.error(f"Failed to save: {e}")
    
    def load(self) -> bool:
        if not Path(self.config.metadata_file).exists():
            return False
        try:
            with open(self.config.metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.texts = data['texts']
                self.word_index = defaultdict(list, data.get('word_index', {}))
            logger.info(f"Loaded: {len(self.texts)} chunks, {len(self.word_index)} words")
            return True
        except Exception as e:
            logger.error(f"Failed to load: {e}")
            return False
    
    def clear(self):
        self.metadata = []
        self.texts = []
        self.word_index = defaultdict(list)
        if Path(self.config.metadata_file).exists():
            Path(self.config.metadata_file).unlink()