# PDF Document Information Extractor

A configurable AI-powered PDF extraction system that uses local LLMs (via Ollama) to extract specific regulatory and compliance information from technical documents. Designed for extracting structured data from material safety data sheets, certificates of analysis, and other compliance documents.

## Features

- **Local AI Processing**: Uses Ollama with Gemma3 - no cloud APIs required
- **Configurable Schemas**: JSON-based schema system for different document types
- **Multiple Document Types**: Pre-built schemas for raw materials, cosmetics, food-grade materials
- **Structured Output**: Extracts data into organized JSON format with evidence tracking
- **Page References**: Tracks which page information was found on
- **Robust Processing**: Handles long documents with timeout management and error recovery

## Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running with Gemma3 model

### Installation

```cmd
# Clone the repository
git clone <your-repo-url>
cd extractor

# Set up virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install langextract PyMuPDF reportlab
```

### Verify Ollama Setup

```cmd
# Check Ollama is running with Gemma3
ollama list

# Test Ollama API
curl http://localhost:11434/api/generate -d "{\"model\": \"gemma3\", \"prompt\": \"test\", \"stream\": false}"
```

### Basic Usage

```cmd
# See available document types
python config_extractor.py --list-schemas

# Extract from a PDF using raw materials schema
python config_extractor.py schemas/raw_materials.json "your_document.pdf" results.json

# Show what a schema will look for
python config_extractor.py schemas/cosmetics_basic.json --info
```

## Document Types

| Schema | Use Case | Requirements Checked |
|--------|----------|---------------------|
| `raw_materials.json` | Chemical/cosmetic raw materials | 17 items: MSDS, REACH, COA, heavy metals, CMR, etc. |
| `cosmetics_basic.json` | Basic cosmetic compliance | 5 items: Safety data, allergens, EU/FDA compliance |
| `food_grade.json` | Food contact materials | 5 items: FDA/EU food contact, heavy metals, certifications |

## Command Reference

### Extract Information
```cmd
python config_extractor.py <schema.json> <document.pdf> [output.json] [options]
```

**Options:**
- `--model gemma3:1b` - Use different Ollama model
- `--model-url http://other-server:11434` - Use different Ollama server

### Information Commands
```cmd
# List all available schemas
python config_extractor.py --list-schemas

# Show detailed schema information
python config_extractor.py schemas/raw_materials.json --info

# Test system setup
python test_extractor.py
```

### Create Test Documents
```cmd
# Generate sample PDFs for testing
python create_schema_test_pdfs.py
```

## Example Usage

### Raw Materials Compliance Check
```cmd
python config_extractor.py schemas/raw_materials.json "supplier_msds.pdf" compliance_check.json
```

This will extract and check for:
- MSDS in English and local languages
- REACH registration numbers
- Heavy metals content
- Certificate of analysis data
- CMR declarations
- Halal/Vegan status
- And 11+ other compliance items

### Basic Cosmetic Ingredient Check
```cmd
python config_extractor.py schemas/cosmetics_basic.json "ingredient_docs.pdf" cosmetic_results.json
```

Checks for essential cosmetic compliance items like EU regulation compliance and allergen information.

## Output Format

Results are saved as JSON with this structure:
```json
{
  "schema_info": {
    "name": "Raw Materials Compliance",
    "description": "Comprehensive regulatory requirements...",
    "extraction_time": null
  },
  "summary": {
    "total_extractions": 8,
    "document_info": "AnnotatedDocument"
  },
  "extractions": [
    {
      "extraction_class": "requirement",
      "extraction_text": "56-81-5",
      "attributes": {
        "name": "CAS Number",
        "status": "present",
        "value": "56-81-5",
        "evidence": "CAS Number: 56-81-5",
        "page_hint": 1
      }
    }
  ]
}
```

## Creating Custom Schemas

To add support for new document types, create a JSON schema file in `schemas/`:

```json
{
  "name": "Your Document Type",
  "description": "What this schema extracts",
  "categories": {
    "safety": {
      "requirement_name": {
        "description": "What to look for",
        "required": true,
        "keywords": ["keyword1", "keyword2"]
      }
    }
  },
  "examples": [...],
  "output_format": {...}
}
```

See existing schemas for complete examples.

## Performance Notes

- **CPU Processing**: Expect 1-2 characters per second on modest hardware
- **Large Documents**: Multi-page PDFs can take 30+ minutes to process
- **Memory Usage**: Model reloads between chunks to prevent memory issues
- **Timeout**: Set to 10 minutes per chunk to handle slow processing

## Troubleshooting

### Common Issues

**"Ollama Model timed out"**
- Check Ollama is running: `ollama list`
- Increase timeout in `base_extractor.py` if needed

**"API key must be provided"**
- Ensure using local model names (not cloud provider formats)
- Verify Ollama server is accessible at `http://localhost:11434`

**"Schema file not found"**
- Check file path: `python config_extractor.py --list-schemas`
- Ensure schema file exists in `schemas/` directory

**Slow processing**
- Normal for CPU processing - consider GPU setup for faster inference
- Use smaller models like `gemma3:1b` for faster processing

### Test Your Setup

```cmd
# Run basic connectivity test
python test_extractor.py

# Test with small document
python config_extractor.py schemas/cosmetics_basic.json test_cosmetics.pdf test_results.json
```

## Architecture

```
extractor/
├── config_extractor.py          # Main configurable extraction script
├── material_extractor.py        # Original monolithic extractor
├── extractors/
│   ├── base_extractor.py        # Common extraction logic
│   ├── schema_extractor.py      # JSON schema loading
│   └── __init__.py
├── schemas/
│   ├── raw_materials.json       # Comprehensive raw material requirements
│   ├── cosmetics_basic.json     # Basic cosmetic compliance
│   └── food_grade.json          # Food-grade material requirements
├── test_*.py                    # Testing utilities
└── venv/                        # Python virtual environment
```

## Contributing

To add new document types:
1. Create a new schema JSON file in `schemas/`
2. Test with sample documents
3. Add to this README's document types table

For issues or questions, check the troubleshooting section or file an issue.

## License

[Add your license information here]