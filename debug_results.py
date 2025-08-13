#!/usr/bin/env python3
"""
Debug script to understand langextract return structure
"""

import sys
import json
from functools import partialmethod

import fitz  # PyMuPDF
import langextract as lx
import langextract.data as lx_data


# Fix timeout and JSON parsing issues with Ollama
class CustomOllamaModel(lx.inference.OllamaLanguageModel):
    def _ollama_query(self, *args, **kwargs):
        kwargs.setdefault('timeout', 600)
        kwargs.setdefault('keep_alive', 0)
        return super()._ollama_query(*args, **kwargs)


# Enable JSON parsing error suppression
lx.resolver.Resolver.resolve = partialmethod(
    lx.resolver.Resolver.resolve, 
    suppress_parse_errors=True
)


def debug_extract():
    # Simple test text
    test_text = """
    Material Safety Data Sheet
    Product Name: Glycerin USP
    CAS Number: 56-81-5
    REACH Registration: 01-2119471987-18-0000
    """
    
    examples = [
        lx_data.ExampleData(
            text="MSDS for Product X, CAS: 123-45-6",
            extractions=[
                lx_data.Extraction(
                    extraction_class="requirement",
                    extraction_text="CAS: 123-45-6",
                    attributes={"name": "CAS Number", "value": "123-45-6"}
                )
            ]
        )
    ]
    
    print("Running extraction...")
    result = lx.extract(
        text_or_documents=test_text,
        prompt_description="Extract CAS number and product info",
        examples=examples,
        language_model_type=CustomOllamaModel,
        model_id="gemma3",
        model_url="http://localhost:11434",
        fence_output=False,
        use_schema_constraints=False,
    )
    
    print(f"\nResult type: {type(result)}")
    print(f"Result dir: {[attr for attr in dir(result) if not attr.startswith('_')]}")
    
    if hasattr(result, 'extractions'):
        print(f"Has extractions: {len(result.extractions)}")
        if result.extractions:
            first_ext = result.extractions[0]
            print(f"First extraction type: {type(first_ext)}")
            print(f"First extraction dir: {[attr for attr in dir(first_ext) if not attr.startswith('_')]}")
            print(f"First extraction class: {getattr(first_ext, 'extraction_class', 'N/A')}")
            print(f"First extraction text: {getattr(first_ext, 'extraction_text', 'N/A')}")
            print(f"First extraction attributes: {getattr(first_ext, 'attributes', 'N/A')}")
    
    # Try to convert to dict
    try:
        result_dict = result.__dict__ if hasattr(result, '__dict__') else str(result)
        print(f"\nResult __dict__: {result_dict}")
    except Exception as e:
        print(f"\nError getting __dict__: {e}")
    
    return result


if __name__ == "__main__":
    debug_extract()