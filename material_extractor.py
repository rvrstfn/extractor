#!/usr/bin/env python3
"""
Raw Material PDF Information Extractor using LangExtract and Gemma3 via Ollama
- FIXED to work with local Ollama without requiring a cloud API key
- Reads PDF text via PyMuPDF (fitz) instead of passing a path
- Adds explicit language_model_type to force Ollama provider
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from functools import partialmethod

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


class RawMaterialExtractor:
    def __init__(self, model_id: str = "gemma3", model_url: str = "http://localhost:11434"):
        self.model_id = model_id
        self.model_url = model_url
        self.examples = self._create_examples()

    def _create_examples(self):
        # Minimal example to steer structure (add more for better recall)
        return [
            lx_data.ExampleData(
                text="Material Safety Data Sheet (MSDS) updated: 2025-03-21 per EU 2020/878. "
                     "REACH status: Registered. Registration No.: 01-2119471987-18-0000",
                extractions=[
                    lx_data.Extraction(
                        extraction_class="requirement",
                        extraction_text="Material Safety Data Sheet (MSDS) updated: 2025-03-21 per EU 2020/878.",
                        attributes={
                            "name": "English and local language MSDS",
                            "status": "present",
                            "applicability": "required",
                            "value": "MSDS present",
                            "details": {"date": "2025-03-21", "regulation": "EU 2020/878"},
                            "evidence": "MSDS updated: 2025-03-21 per EU 2020/878",
                            "page_hint": 1
                        }
                    ),
                    lx_data.Extraction(
                        extraction_class="requirement",
                        extraction_text="REACH status: Registered. Registration No.: 01-2119471987-18-0000",
                        attributes={
                            "name": "REACH Declaration and registration Number",
                            "status": "present",
                            "applicability": "required",
                            "value": "Registered",
                            "details": {"registration_no": "01-2119471987-18-0000"},
                            "evidence": "REACH status: Registered. Registration No.: ...",
                            "page_hint": 1
                        }
                    ),
                ],
            )
        ]

    def _create_extraction_prompt(self) -> str:
        return """
You are extracting a compliance/checklist report from a raw material dossier.

RULES
- Extract ONLY facts explicitly present in the text. No guesses.
- Use exact substrings from the document as `extraction_text` where possible.
- If an item is not present, create an entry with status="not_found".
- If the item is conditionally applicable (e.g., ONLY for colorants / silicone / marine / fragrance / polymer / veg/biotech / synthetic wax), set applicability accordingly:
  - applicability: "required", "not_applicable", or "unknown"
- Normalize values when obvious (CAS/EC formats, dates yyyy-mm-dd), but keep a source `evidence` snippet.
- For lists like contaminants (PAHs, benzene, phthalates, etc.), aggregate in attributes.details as per-item keys.
- Prefer most recent dates if multiple are present.

OUTPUT
- Use one extraction class named "requirement".
- attributes:
  {"name": <one of the checklist items>,
   "status": "present"|"not_found",
   "applicability": "required"|"not_applicable"|"unknown",
   "value": <primary value or None>,
   "details": <dict of structured fields>,
   "evidence": <short exact quote>,
   "page_hint": <page number from '===== PAGE N =====' if possible>}
"""

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract raw material information from a PDF document using local Ollama."""
        try:
            text = pdf_to_text_with_pages(pdf_path)
            extraction_prompt = self._create_extraction_prompt()

            result = lx.extract(
                text_or_documents=text,
                prompt_description=extraction_prompt,
                examples=self.examples,
                # Use custom timeout model instead of default:
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
    def save_results(results, output_path: str):
        # Convert langextract results to JSON-serializable format
        serializable_results = {}
        
        # Check if it's an error dict first
        if isinstance(results, dict) and "error" in results:
            serializable_results = results
        else:
            # Handle AnnotatedDocument or similar langextract objects
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
                    # Complete fallback
                    serializable_results = {"raw_result": str(results)}
                    
            except Exception as e:
                serializable_results = {"conversion_error": str(e), "raw_result": str(results)}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) < 2:
        print('Usage: python material_extractor.py "<pdf_path_with_spaces>" [output.json] [model_tag]')
        sys.exit(1)

    # Accept quoted path with spaces; recommend quoting in Windows shell.
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "extraction_results.json"
    model_tag = sys.argv[3] if len(sys.argv) > 3 else "gemma3"

    extractor = RawMaterialExtractor(model_id=model_tag)
    print(f"Processing PDF: {pdf_path}")
    print(f"Using model: {model_tag} at http://localhost:11434")

    results = extractor.extract_from_pdf(pdf_path)
    RawMaterialExtractor.save_results(results, output_path)

    # Check if it's an error dict or AnnotatedDocument
    if isinstance(results, dict) and "error" in results:
        print(f"\nExtraction FAILED: {results['error']}")
    else:
        extraction_count = len(results.extractions) if hasattr(results, 'extractions') else 0
        print(f"\nExtraction OK. Found {extraction_count} extractions. Results saved to: {output_path}")


if __name__ == "__main__":
    main()
