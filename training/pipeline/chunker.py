import re
import tiktoken
from typing import List, Tuple
from .schemas import Chunk, Message

class MarkdownChunker:
    def __init__(self, max_tokens: int = 512, model_name: str = "gpt-3.5-turbo"):
        self.max_tokens = max_tokens
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def _split_into_blocks(self, text: str) -> List[Tuple[str, int, int]]:
        """Splits text into semantic blocks with offsets."""
        blocks = []
        special_pattern = re.compile(r'(```[\s\S]*?```|\$\$[\s\S]*?\$\$|^(?:#{1,6})\s+.*?$)', re.MULTILINE)
        
        last_end = 0
        for match in special_pattern.finditer(text):
            start = match.start()
            end = match.end()
            
            if start > last_end:
                pre_text = text[last_end:start]
                para_start = last_end
                for para in re.split(r'(\n\s*\n)', pre_text):
                    para_len = len(para)
                    if para.strip():
                        blocks.append((para, para_start, para_start + para_len))
                    para_start += para_len
                    
            block_text = match.group(0)
            blocks.append((block_text, start, end))
            last_end = end
            
        if last_end < len(text):
            post_text = text[last_end:]
            para_start = last_end
            for para in re.split(r'(\n\s*\n)', post_text):
                para_len = len(para)
                if para.strip():
                    blocks.append((para, para_start, para_start + para_len))
                para_start += para_len
                
        return blocks

    def _merge_blocks(self, blocks: List[Tuple[str, int, int]], original_text: str) -> List[Tuple[str, int, int, str]]:
        merged = []
        current_section = None
        
        current_chunk_start = -1
        current_chunk_end = -1
        
        for text, start, end in blocks:
            heading_match = re.match(r'^(#{1,6})\s+(.*)$', text.strip())
            
            if heading_match:
                if current_chunk_start != -1:
                    chunk_text = original_text[current_chunk_start:current_chunk_end]
                    if chunk_text.strip():
                        merged.append((chunk_text, current_chunk_start, current_chunk_end, current_section))
                
                current_section = heading_match.group(2).strip()
                current_chunk_start = start
                current_chunk_end = end
                continue
                
            if current_chunk_start == -1:
                current_chunk_start = start
                current_chunk_end = end
            else:
                merged_text = original_text[current_chunk_start:end]
                if self.count_tokens(merged_text) <= self.max_tokens:
                    current_chunk_end = end
                else:
                    chunk_text = original_text[current_chunk_start:current_chunk_end]
                    if chunk_text.strip():
                        merged.append((chunk_text, current_chunk_start, current_chunk_end, current_section))
                    current_chunk_start = start
                    current_chunk_end = end

        if current_chunk_start != -1:
            chunk_text = original_text[current_chunk_start:current_chunk_end]
            if chunk_text.strip():
                merged.append((chunk_text, current_chunk_start, current_chunk_end, current_section))
            
        return merged

    def chunk_message(self, message: Message, sample_id: str, msg_index: int) -> List[Chunk]:
        """Chunks a single message and returns Chunk objects."""
        original_text = message.content
        blocks = self._split_into_blocks(original_text)
        merged = self._merge_blocks(blocks, original_text)
        
        chunks = []
        for i, (text, start, end, section) in enumerate(merged):
            chunk = Chunk(
                chunk_id=f"{sample_id}_msg{msg_index}_chunk{i:03d}",
                text=text,
                role=message.role,
                section=section,
                start_offset=start,
                end_offset=end,
                token_count=self.count_tokens(text)
            )
            chunks.append(chunk)
            
        return chunks
