"""
Text chunking utilities module.
Helper functions for splitting text into chunks for embedding.
"""

from typing import List
import re


def chunk_text_by_sentences(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks based on sentence boundaries.
    
    Args:
        text: Input text to chunk
        chunk_size: Target chunk size in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Split by sentences (simple approach)
    sentences = re.split(r'[.!?]+\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_length = len(sentence) + 2  # +2 for period and space
        
        if current_length + sentence_length > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = ". ".join(current_chunk) + "."
            chunks.append(chunk_text)
            
            # Start new chunk with overlap
            overlap_sentences = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_sentences
            current_length = sum(len(s) + 2 for s in overlap_sentences)
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    # Add final chunk
    if current_chunk:
        chunk_text = ". ".join(current_chunk) + "."
        chunks.append(chunk_text)
    
    return chunks


def chunk_text_by_words(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks based on word boundaries.
    
    Args:
        text: Input text to chunk
        chunk_size: Target chunk size in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Overlap: keep last N words
            overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_words
            current_length = sum(len(w) + 1 for w in overlap_words)
        
        current_chunk.append(word)
        current_length += word_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

