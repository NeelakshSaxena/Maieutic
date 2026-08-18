import pytest
from training.pipeline.chunker import MarkdownChunker
from training.pipeline.schemas import Message

def test_markdown_chunker():
    chunker = MarkdownChunker(max_tokens=50)
    
    text = r"""# Binary Search
Binary search is an algorithm.
It works on sorted arrays.

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

Here is a math equation:
$$
O(\log n)
$$
"""
    msg = Message(role="assistant", content=text)
    chunks = chunker.chunk_message(msg, "sample1", 0)
    
    assert len(chunks) > 0
    assert chunks[0].section == "Binary Search"
    
    for chunk in chunks:
        assert chunk.text == text[chunk.start_offset:chunk.end_offset]
        assert "```python" in chunk.text or "O(\\log n)" in chunk.text or "algorithm" in chunk.text

def test_chunker_preserves_code_fences():
    chunker = MarkdownChunker(max_tokens=10)
    text = "Intro text.\n\n```python\nprint('hello')\nprint('world')\n```\n\nOutro text."
    msg = Message(role="assistant", content=text)
    chunks = chunker.chunk_message(msg, "sample2", 0)
    
    assert len(chunks) == 3
    assert chunks[1].text == "```python\nprint('hello')\nprint('world')\n```"
    assert chunks[1].start_offset == text.find("```python")
