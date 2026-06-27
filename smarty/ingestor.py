import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import PyPDF2
import docx
import pandas as pd
from bs4 import BeautifulSoup
import html2text
from smarty.config import Config

logger = logging.getLogger(__name__)

class Ingestor:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def load(self, directory: str = None) -> Dict[str, str]:
        directory = directory or self.config.docs_dir
        docs = {}
        path = Path(directory)
        if not path.exists():
            logger.error(f"Directory not found: {directory}")
            return docs
        files = []
        for ext in self.config.supported_formats:
            files.extend(path.glob(f"*{ext}"))
        if not files:
            logger.warning(f"No supported files found in {directory}")
            return docs
        logger.info(f"Found {len(files)} files to process")
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            results = executor.map(self._load_file, files)
            for file_path, text in results:
                if text and text.strip():
                    docs[str(file_path)] = text.strip()
        logger.info(f"Loaded {len(docs)} documents")
        return docs
    
    def _load_file(self, file_path: Path) -> Tuple[str, str]:
        suffix = file_path.suffix.lower()
        file_path_str = str(file_path)
        try:
            if suffix == '.pdf':
                text = self._read_pdf(file_path)
            elif suffix == '.docx':
                text = self._read_docx(file_path)
            elif suffix in ['.html', '.htm']:
                text = self._read_html(file_path)
            elif suffix == '.json':
                text = self._read_json(file_path)
            elif suffix == '.csv':
                text = self._read_csv(file_path)
            else:
                text = self._read_txt(file_path)
            return file_path_str, text
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")
            return file_path_str, ""
    
    def _read_pdf(self, path: Path) -> str:
        text = ""
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    try:
                        text += page.extract_text() + "\n"
                    except:
                        continue
        except Exception as e:
            logger.error(f"PDF error {path.name}: {e}")
        return text
    
    def _read_docx(self, path: Path) -> str:
        try:
            doc = docx.Document(path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            logger.error(f"DOCX error {path.name}: {e}")
            return ""
    
    def _read_txt(self, path: Path) -> str:
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                with open(path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
    
    def _read_html(self, path: Path) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            logger.error(f"HTML error {path.name}: {e}")
            return ""
    
    def _read_json(self, path: Path) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            def extract(obj, prefix=""):
                parts = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        parts.extend(extract(v, f"{prefix}{k}: "))
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        parts.extend(extract(v, f"{prefix}[{i}] "))
                elif isinstance(obj, str):
                    if len(obj) > 10:
                        parts.append(f"{prefix}{obj}")
                elif isinstance(obj, (int, float, bool)):
                    parts.append(f"{prefix}{str(obj)}")
                return parts
            return "\n".join(extract(data))
        except Exception as e:
            logger.error(f"JSON error {path.name}: {e}")
            return ""
    
    def _read_csv(self, path: Path) -> str:
        try:
            df = pd.read_csv(path)
            parts = [" | ".join(df.columns.tolist())]
            for _, row in df.head(1000).iterrows():
                parts.append(" | ".join([str(v) for v in row.values]))
            return "\n".join(parts)
        except Exception as e:
            logger.error(f"CSV error {path.name}: {e}")
            return ""
