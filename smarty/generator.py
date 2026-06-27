"""
generator.py - Fast, No-LLM Generator
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Generator:
    def __init__(self, config):
        self.config = config
        self.llm_loaded = False
    
    def generate(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context:
            return {
                'response': 'No relevant information found.',
                'confidence': 0.0,
                'sources': []
            }
        
        response_parts = []
        sources = []
        
        for i, chunk in enumerate(context[:5]):
            source = chunk.get('source', f'Document {i+1}')
            sources.append(source)
            text = chunk.get('text', '')
            score = chunk.get('score', 0)
            
            text = ' '.join(text.split())
            if len(text) > 400:
                text = text[:400] + '...'
            
            response_parts.append(
                f"[{i+1}] {source} (relevance: {score:.2f})\n{text}\n"
            )
        
        response = '\n\n'.join(response_parts)
        confidence = sum([c.get('score', 0) for c in context[:3]]) / 3
        
        return {
            'response': f"Found {len(context)} relevant passages:\n\n{response}",
            'confidence': min(1.0, confidence),
            'sources': list(set(sources[:3]))
        }