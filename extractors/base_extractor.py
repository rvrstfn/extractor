#!/usr/bin/env python3
"""
Base extractor class with common extraction logic
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from functools import partialmethod
from abc import ABC, abstractmethod

import fitz  # PyMuPDF
import langextract as lx
import langextract.data as lx_data


# Fix timeout and JSON parsing issues with Ollama
class CustomOllamaModel(lx.inference.OllamaLanguageModel):
    def _ollama_query(self, *args, **kwargs):
        kwargs.setdefault('timeout', 600)  # 10 minutes instead of 30 seconds
        kwargs.setdefault('keep_alive', 0)  # Reload model each time to avoid memory issues
        return super()._ollama_query(*args, **kwargs)


# Enable JSON parsing error suppression
lx.resolver.Resolver.resolve = partialmethod(
    lx.resolver.Resolver.resolve, 
    suppress_parse_errors=True
)


def pdf_to_text_with_pages(pdf_path: str) -> str:
    """Extract text from PDF and add clear page markers to help page grounding."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        hdr = f"\n\n===== PAGE {i+1} =====\n"
        txt = page.get_text("text") or ""
        pages.append(hdr + txt)
    return "\n".join(pages)


class BaseExtractor(ABC):
    """Base class for document extractors with common functionality"""
    
    def __init__(self, model_id: str = "gemma3", model_url: str = "http://localhost:11434"):
        self.model_id = model_id
        self.model_url = model_url
        self.schema = None
        self.examples = []
        
    @abstractmethod
    def load_schema(self, schema_source) -> Dict[str, Any]:
        """Load extraction schema - to be implemented by subclasses"""
        pass
    
    def create_examples_from_schema(self) -> List[lx_data.ExampleData]:
        """Create examples from schema definition"""
        if not self.schema or 'examples' not in self.schema:
            return []
        
        examples = []
        for example_data in self.schema['examples']:
            extractions = []
            for ext_data in example_data['extractions']:
                extraction = lx_data.Extraction(
                    extraction_class=ext_data['extraction_class'],
                    extraction_text=ext_data['extraction_text'],
                    attributes=ext_data['attributes']
                )
                extractions.append(extraction)
            
            example = lx_data.ExampleData(
                text=example_data['text'],
                extractions=extractions
            )
            examples.append(example)
        
        return examples
    
    def create_extraction_prompt(self) -> str:
        """Create extraction prompt from schema"""
        if not self.schema:
            return "Extract relevant information from the document."
        
        schema_name = self.schema.get('name', 'Document')
        description = self.schema.get('description', '')
        
        prompt = f"""
You are extracting information from {schema_name.lower()} documentation.
{description}

Extract information according to these categories:
"""
        
        for category_name, category_items in self.schema.get('categories', {}).items():
            prompt += f"\n{category_name.upper()}:\n"
            for item_name, item_config in category_items.items():
                required_text = " (REQUIRED)" if item_config.get('required', False) else " (optional)"
                prompt += f"- {item_config['description']}{required_text}\n"
                if 'keywords' in item_config:
                    prompt += f"  Keywords: {', '.join(item_config['keywords'])}\n"
        
        # Add output format instructions
        output_format = self.schema.get('output_format', {})
        if output_format:
            prompt += f"""
OUTPUT FORMAT:
- Use extraction class: "{output_format.get('extraction_class', 'requirement')}"
- For each item found, include these attributes:
"""
            for attr_name, attr_type in output_format.get('attributes_schema', {}).items():
                prompt += f"  - {attr_name}: {attr_type}\n"
        
        prompt += """
If information is not available, mark status as "not_found".
If information is not applicable to this document type, mark status as "not_applicable".
Include exact text quotes as evidence where possible.
"""
        
        return prompt
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract information from PDF using loaded schema"""
        if not self.schema:
            return {"error": "No schema loaded"}
        
        try:
            text = pdf_to_text_with_pages(pdf_path)
            extraction_prompt = self.create_extraction_prompt()
            
            result = lx.extract(
                text_or_documents=text,
                prompt_description=extraction_prompt,
                examples=self.examples,
                language_model_type=CustomOllamaModel,
                model_id=self.model_id,
                model_url=self.model_url,
                fence_output=False,
                use_schema_constraints=False,
                extraction_passes=2,
                max_workers=8,
                max_char_buffer=1200,
            )
            return result
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def save_results(results, output_path: str, schema_info: Dict = None):
        """Save extraction results to JSON with schema metadata"""
        serializable_results = {}
        
        # Add schema metadata if provided
        if schema_info:
            serializable_results["schema_info"] = {
                "name": schema_info.get('name', 'Unknown'),
                "description": schema_info.get('description', ''),
                "extraction_time": None  # Could add timestamp here
            }
        
        # Handle results
        if isinstance(results, dict) and "error" in results:
            serializable_results["error"] = results["error"]
        else:
            try:
                if hasattr(results, 'extractions'):
                    serializable_results["extractions"] = []
                    serializable_results["summary"] = {
                        "total_extractions": len(results.extractions) if results.extractions else 0,
                        "document_info": str(type(results).__name__)
                    }
                    
                    for extraction in results.extractions:
                        ext_data = {
                            "extraction_class": getattr(extraction, 'extraction_class', ''),
                            "extraction_text": getattr(extraction, 'extraction_text', ''),
                            "attributes": getattr(extraction, 'attributes', {}),
                            "document_id": getattr(extraction, 'document_id', ''),
                        }
                        serializable_results["extractions"].append(ext_data)
                else:
                    serializable_results = {"raw_result": str(results)}
                    
            except Exception as e:
                serializable_results = {"conversion_error": str(e), "raw_result": str(results)}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)