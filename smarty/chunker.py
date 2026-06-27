import re
from typing import List
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    nltk.data.find('tokenizers/punkt')
except:
    try:
        nltk.download('punkt', quiet=True)
        from nltk.tokenize import sent_tokenize
    except:
        def sent_tokenize(text):
            return re.split(r'(?<=[.!?])\s+', text)

class Chunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk = 50
    
    def chunk(self, text: str) -> List[str]:
        if not text or len(text.strip()) < self.min_chunk:
            return []
        chunks = self._semantic_chunk(text)
        if not chunks:
            chunks = self._fixed_chunk(text)
        return [c for c in chunks if len(c.strip()) >= self.min_chunk]
    
    def _semantic_chunk(self, text: str) -> List[str]:
        try:
            sentences = sent_tokenize(text)
        except:
            sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""
        for sent in sentences:
            if len(current) + len(sent) > self.chunk_size and current:
                chunks.append(current.strip())
                current = self._get_overlap(current) + " " + sent
            else:
                current += " " + sent if current else sent
        if current:
            chunks.append(current.strip())
        return chunks
    
    def _fixed_chunk(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                search = text[max(start, end - 100):end]
                matches = list(re.finditer(r'[.!?]\s+', search))
                if matches:
                    end = start + max(0, search.rfind(matches[-1].group()) + len(matches[-1].group()))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - self.overlap if end < len(text) else end
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        if self.overlap <= 0:
            return ""
        overlap = text[-self.overlap:]
        sentences = re.split(r'(?<=[.!?])\s+', overlap)
        if len(sentences) > 1:
            return " ".join(sentences[-2:])
        else:
            return overlap[-self.overlap:]
