# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a raw material PDF information extractor for cosmetic/chemical ingredients. It uses LangExtract with local Ollama models (Gemma3) to extract regulatory compliance information from material safety data sheets and certificates.

The system extracts specific regulatory requirements including MSDS data, REACH declarations, certificates of analysis, heavy metals content, GMO status, and numerous other compliance items required for cosmetic ingredient documentation.

## Setup Commands

**Environment Setup:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install langextract PyMuPDF reportlab
```

**Verify Ollama Setup:**
```cmd
ollama list
curl http://localhost:11434/api/generate -d "{\"model\": \"gemma3\", \"prompt\": \"test\", \"stream\": false}"
```

**Test Installation:**
```cmd
python test_extractor.py
```

## Core Usage

**Extract from PDF:**
```cmd
python material_extractor.py "document.pdf" output_results.json [model_name]
```

**Create Test PDF:**
```cmd
python create_test_pdf.py
```

**Debug Extraction Results:**
```cmd
python debug_results.py
```

## Architecture

### Core Components

- **CustomOllamaModel**: Extends langextract's OllamaLanguageModel with 10-minute timeout and `keep_alive=0` to prevent GPU memory issues
- **RawMaterialExtractor**: Main extraction class containing comprehensive schema for regulatory requirements
- **pdf_to_text_with_pages()**: Uses PyMuPDF to extract text with page markers for better grounding

### Key Implementation Details

**Ollama Integration Fixes:**
- Uses explicit `language_model_type=CustomOllamaModel` to force local provider
- JSON parsing error suppression via `suppress_parse_errors=True` 
- Extended timeout (600s) and model reloading to handle long documents

**Extraction Schema:**
The system defines 9 main categories of requirements:
- `general_documents`: MSDS, REACH, COA, heavy metals, etc.
- `vegetable_biotech_origin`: Bio certificates, RSPO, GMO declarations
- `colorant_pearls`: Nanomaterial declarations, purity statements
- `titanium_dioxide_colorant` & `titanium_dioxide_sunscreen`: Specific TiO2 compliance
- `silica_present`: Crystalline structure certificates
- `polymer`: Monomer content, molecular weight
- `fragrances_essential_oils`: Allergen content, IFRA compliance
- `synthetic_waxes`: Cosmetics Europe compliance

**Result Processing:**
LangExtract returns `AnnotatedDocument` objects with `.extractions` list. Each extraction has:
- `.extraction_class`: Category name
- `.extraction_text`: Extracted text snippet  
- `.attributes`: Structured data (name, status, value, evidence, page_hint)

## Dependencies

**Required Ollama Models:**
- `gemma3:latest` (primary)
- Alternative: `gemma3:1b`, `exaone-deep:2.4b`

**Python Packages:**
- `langextract`: Core extraction engine
- `PyMuPDF (fitz)`: PDF text extraction
- `reportlab`: Test PDF generation

## Performance Considerations

- CPU-only processing is very slow (1 char/sec on modest hardware)
- Large PDFs can take 1+ hours to process
- Memory usage increases with document size due to langextract's chunking approach
- Model reloading (`keep_alive=0`) trades speed for reliability on long extractions