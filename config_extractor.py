#!/usr/bin/env python3
"""
Configurable PDF extractor that uses JSON schema files
"""

import sys
import argparse
from pathlib import Path

from extractors import SchemaExtractor


def list_available_schemas(schemas_dir: Path) -> None:
    """List all available schema files"""
    print("Available schemas:")
    schema_files = list(schemas_dir.glob("*.json"))
    
    if not schema_files:
        print("  No schema files found in schemas/ directory")
        return
    
    for schema_file in sorted(schema_files):
        try:
            extractor = SchemaExtractor()
            extractor.load_schema(str(schema_file))
            schema_info = extractor.get_schema_info()
            
            print(f"  {schema_file.stem}:")
            print(f"    Name: {schema_info.get('name', 'N/A')}")
            print(f"    Description: {schema_info.get('description', 'N/A')}")
            print(f"    Categories: {len(schema_info.get('categories', []))}")
            print(f"    Total requirements: {schema_info.get('total_requirements', 0)}")
            print()
        except Exception as e:
            print(f"  {schema_file.stem}: Error loading - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract information from PDFs using configurable schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available schemas
  python config_extractor.py --list-schemas
  
  # Extract using specific schema
  python config_extractor.py schemas/raw_materials.json document.pdf
  
  # Extract with custom output file
  python config_extractor.py schemas/cosmetics_basic.json doc.pdf results.json
  
  # Use different model
  python config_extractor.py schemas/food_grade.json doc.pdf --model gemma3:1b
"""
    )
    
    parser.add_argument('schema', nargs='?', help='Schema JSON file to use')
    parser.add_argument('pdf_path', nargs='?', help='PDF file to extract from')
    parser.add_argument('output', nargs='?', default='extraction_results.json',
                       help='Output JSON file (default: extraction_results.json)')
    
    parser.add_argument('--list-schemas', action='store_true',
                       help='List all available schema files')
    parser.add_argument('--model', default='gemma3',
                       help='Ollama model to use (default: gemma3)')
    parser.add_argument('--model-url', default='http://localhost:11434',
                       help='Ollama server URL (default: http://localhost:11434)')
    parser.add_argument('--info', action='store_true',
                       help='Show schema information without extracting')
    
    args = parser.parse_args()
    
    # Handle list schemas
    if args.list_schemas:
        schemas_dir = Path('schemas')
        if not schemas_dir.exists():
            print("Error: schemas/ directory not found")
            sys.exit(1)
        list_available_schemas(schemas_dir)
        return
    
    # Validate required arguments
    if not args.schema:
        print("Error: schema file is required (use --list-schemas to see available)")
        parser.print_help()
        sys.exit(1)
    
    # Show schema info only
    if args.info:
        try:
            extractor = SchemaExtractor(args.schema, args.model, args.model_url)
            schema_info = extractor.get_schema_info()
            
            print(f"Schema: {schema_info.get('name', 'N/A')}")
            print(f"Description: {schema_info.get('description', 'N/A')}")
            print(f"Categories: {', '.join(schema_info.get('categories', []))}")
            print(f"Total requirements: {schema_info.get('total_requirements', 0)}")
            
            # Show detailed breakdown
            if extractor.schema and 'categories' in extractor.schema:
                print("\nDetailed requirements:")
                for category, items in extractor.schema['categories'].items():
                    print(f"  {category}: {len(items)} items")
                    for item_name, item_config in items.items():
                        required = " (required)" if item_config.get('required', False) else ""
                        print(f"    - {item_name}: {item_config.get('description', 'N/A')}{required}")
            
        except Exception as e:
            print(f"Error loading schema: {e}")
            sys.exit(1)
        return
    
    if not args.pdf_path:
        print("Error: PDF path is required")
        parser.print_help()
        sys.exit(1)
    
    # Validate files exist
    schema_path = Path(args.schema)
    pdf_path = Path(args.pdf_path)
    
    if not schema_path.exists():
        print(f"Error: Schema file not found: {args.schema}")
        sys.exit(1)
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Perform extraction
    try:
        print(f"Loading schema: {args.schema}")
        extractor = SchemaExtractor(args.schema, args.model, args.model_url)
        schema_info = extractor.get_schema_info()
        
        print(f"Schema loaded: {schema_info.get('name', 'Unknown')}")
        print(f"Total requirements: {schema_info.get('total_requirements', 0)}")
        
        print(f"\nProcessing PDF: {args.pdf_path}")
        print(f"Using model: {args.model} at {args.model_url}")
        
        results = extractor.extract_from_pdf(str(pdf_path))
        
        # Save results with schema metadata
        extractor.save_results(results, args.output, schema_info)
        
        # Print summary
        if isinstance(results, dict) and "error" in results:
            print(f"\nExtraction FAILED: {results['error']}")
            sys.exit(1)
        else:
            extraction_count = len(results.extractions) if hasattr(results, 'extractions') else 0
            print(f"\nExtraction completed successfully!")
            print(f"Found {extraction_count} extractions")
            print(f"Results saved to: {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()