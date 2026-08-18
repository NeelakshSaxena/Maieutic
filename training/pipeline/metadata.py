import re
from .schemas import Chunk, ProcessedSample

def add_chunk_metadata(sample: ProcessedSample):
    """
    Enriches chunks with deterministic metadata.
    """
    for chunk in sample.chunks:
        has_code = bool(re.search(r'```[\s\S]*?```', chunk.text))
        has_math = bool(re.search(r'\$\$[\s\S]*?\$\$', chunk.text))
        
        # Word count approximation
        word_count = len(re.findall(r'\w+', chunk.text))
        # Avg reading speed ~ 238 words per minute -> ~4 words per second
        reading_time_sec = word_count / 4.0
        
        chunk.metadata.update({
            "contains_code": has_code,
            "contains_math": has_math,
            "word_count": word_count,
            "estimated_reading_time_sec": round(reading_time_sec, 2)
        })
        
        # Inherit language from parent if not specified
        if not chunk.language:
            # Check for specific language in code blocks
            code_lang_match = re.search(r'```(\w+)', chunk.text)
            if code_lang_match:
                chunk.language = code_lang_match.group(1).lower()
            else:
                chunk.language = "en" # Fallback
