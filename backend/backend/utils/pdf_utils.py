"""
PDF utilities module.
Helper functions for PDF processing and text extraction.
"""

from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
import camelot


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract plain text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Extracted text as string
    """
    text_parts = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    return "\n\n".join(text_parts)


def extract_tables_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract tables from PDF using both camelot and pdfplumber.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        List of table dictionaries
    """
    tables = []
    
    # Try camelot first
    try:
        camelot_tables = camelot.read_pdf(str(pdf_path), pages="all")
        for table in camelot_tables:
            df = table.df
            tables.append({
                "source": "camelot",
                "page": table.page,
                "data": df.to_dict("records"),
                "raw_df": df
            })
    except Exception as e:
        print(f"Camelot extraction failed: {e}")
    
    # Fallback to pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        tables.append({
                            "source": "pdfplumber",
                            "page": page_num,
                            "data": table
                        })
    except Exception as e:
        print(f"PDFPlumber extraction failed: {e}")
    
    return tables

