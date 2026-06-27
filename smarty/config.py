from dataclasses import dataclass, field
from typing import Set
import torch

@dataclass
class Config:
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "microsoft/DialoGPT-medium"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    chunk_size: int = 512
    chunk_overlap: int = 50
    min_chunk_size: int = 50
    top_k: int = 5
    similarity_threshold: float = 0.3
    temperature: float = 0.3
    max_new_tokens: int = 256
    top_p: float = 0.95
    repetition_penalty: float = 1.1
    docs_dir: str = "knowledge_base"
    data_dir: str = "data"
    vector_index: str = "data/index.faiss"
    metadata_file: str = "data/metadata.pkl"
    batch_size: int = 32
    max_workers: int = 4
    history_size: int = 10
    supported_formats: Set[str] = field(default_factory=lambda: {'.pdf', '.txt', '.docx', '.html', '.json', '.csv', '.md'})
    
    def __post_init__(self):
        from pathlib import Path
        Path(self.data_dir).mkdir(exist_ok=True)
        Path(self.docs_dir).mkdir(exist_ok=True)
