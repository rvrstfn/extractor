#!/usr/bin/env python3
"""
Test script for the Raw Material PDF Extractor
"""

import langextract as lx
import langextract.data as lx_data
from material_extractor import RawMaterialExtractor

def test_ollama_connection():
    """Test connection to Ollama"""
    print("Testing Ollama connection...")
    
    try:
        # Simple test extraction
        test_text = """
        Material Safety Data Sheet (MSDS)
        Product Name: Glycerin USP
        CAS Number: 56-81-5
        EINECS: 200-289-5
        Composition: 99.7% Glycerin
        Country of Origin: USA
        Heavy Metals: <10ppm
        GMO Status: GMO-free
        Halal Certified: Yes
        """
        
        # Create simple example for testing
        examples = [
            lx_data.ExampleData(
                text="Product Name: Test Chemical\nCAS Number: 123-45-6",
                extractions=[
                    lx_data.Extraction(
                        extraction_class="product_name",
                        extraction_text="Test Chemical",
                        attributes={}
                    )
                ]
            )
        ]
        
        result = lx.extract(
            text_or_documents=test_text,
            prompt_description="Extract product information from material safety data sheet",
            examples=examples,
            model_id="gemma3:latest",
            model_url="http://localhost:11434",
            api_key=None,
            fence_output=False,
            use_schema_constraints=False
        )
        
        print("Ollama connection successful!")
        print("Test extraction result:")
        print(result)
        return True
        
    except Exception as e:
        print(f"Ollama connection failed: {str(e)}")
        return False

def test_extractor_class():
    """Test the RawMaterialExtractor class"""
    print("\nTesting RawMaterialExtractor class...")
    
    try:
        extractor = RawMaterialExtractor()
        print(f"Extractor initialized with model: {extractor.model_id}")
        print(f"Schema contains {len(extractor.extraction_schema)} main categories")
        return True
        
    except Exception as e:
        print(f"Extractor initialization failed: {str(e)}")
        return False

def main():
    print("Testing Raw Material PDF Extractor Setup\n")
    
    # Test Ollama connection
    ollama_ok = test_ollama_connection()
    
    # Test extractor class
    extractor_ok = test_extractor_class()
    
    print(f"\nTest Results:")
    print(f"Ollama Connection: {'PASS' if ollama_ok else 'FAIL'}")
    print(f"Extractor Class: {'PASS' if extractor_ok else 'FAIL'}")
    
    if ollama_ok and extractor_ok:
        print(f"\nAll tests passed! Your setup is ready to use.")
        print(f"\nTo extract from a PDF, run:")
        print(f"python material_extractor.py <path_to_pdf>")
    else:
        print(f"\nSome tests failed. Please check your setup.")

if __name__ == "__main__":
    main()