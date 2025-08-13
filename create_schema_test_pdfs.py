#!/usr/bin/env python3
"""
Create test PDFs for different schema types
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_cosmetics_test_pdf():
    """Create test PDF for cosmetics schema"""
    filename = "test_cosmetics.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    
    c.drawString(100, 750, "COSMETIC INGREDIENT COMPLIANCE DOCUMENT")
    c.drawString(100, 720, "Product: Hyaluronic Acid Serum Base")
    c.drawString(100, 700, "")
    c.drawString(100, 680, "SAFETY INFORMATION:")
    c.drawString(100, 660, "Material Safety Data Sheet: Available")
    c.drawString(100, 640, "Allergen Status: No known allergens present")
    c.drawString(100, 620, "Preservative System: Phenoxyethanol 0.5%")
    c.drawString(100, 600, "")
    c.drawString(100, 580, "REGULATORY COMPLIANCE:")
    c.drawString(100, 560, "EU Cosmetics Regulation 1223/2009: Compliant")
    c.drawString(100, 540, "FDA Cosmetics: GRAS status confirmed")
    c.drawString(100, 520, "Notification: CPNP-123456789")
    
    c.save()
    print(f"Created cosmetics test PDF: {filename}")


def create_food_grade_test_pdf():
    """Create test PDF for food grade schema"""
    filename = "test_food_grade.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    
    c.drawString(100, 750, "FOOD GRADE MATERIAL CERTIFICATION")
    c.drawString(100, 720, "Product: Food Grade Silicone Additive")
    c.drawString(100, 700, "")
    c.drawString(100, 680, "FOOD SAFETY COMPLIANCE:")
    c.drawString(100, 660, "FDA Food Contact: Approved under 21 CFR 175.300")
    c.drawString(100, 640, "EU Food Contact: Complies with Regulation 10/2011/EU")
    c.drawString(100, 620, "Migration Test: <10ppb overall migration")
    c.drawString(100, 600, "Heavy Metals Analysis:")
    c.drawString(100, 580, "  Lead: <0.1 ppm")
    c.drawString(100, 560, "  Cadmium: <0.05 ppm")
    c.drawString(100, 540, "")
    c.drawString(100, 520, "CERTIFICATIONS:")
    c.drawString(100, 500, "Kosher: Certified by OK Kosher (expires 2025-12-31)")
    c.drawString(100, 480, "Halal: Certified by Islamic Society")
    
    c.save()
    print(f"Created food grade test PDF: {filename}")


def create_comprehensive_test_pdf():
    """Create comprehensive test PDF with multiple schema elements"""
    filename = "test_comprehensive.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1 - Basic info
    c.drawString(100, 750, "COMPREHENSIVE MATERIAL DOCUMENTATION")
    c.drawString(100, 720, "Product: Multi-functional Cosmetic Emulsifier")
    c.drawString(100, 700, "CAS Number: 61789-40-0")
    c.drawString(100, 680, "INCI Name: Cetearyl Alcohol (and) Cetearyl Glucoside")
    c.drawString(100, 660, "")
    c.drawString(100, 640, "REGULATORY STATUS:")
    c.drawString(100, 620, "REACH Registration: 01-2119484862-27-0000")
    c.drawString(100, 600, "EU Cosmetics Regulation 1223/2009: Approved")
    c.drawString(100, 580, "China CSAR: Compliant with Annex 14")
    c.drawString(100, 560, "FDA Status: GRAS for cosmetic use")
    c.drawString(100, 540, "")
    c.drawString(100, 520, "SAFETY DATA:")
    c.drawString(100, 500, "MSDS: Available in English and local languages")
    c.drawString(100, 480, "CMR Status: CMR-free certified")
    c.drawString(100, 460, "Heavy Metals: All <10ppm")
    
    c.showPage()  # New page
    
    # Page 2 - Certifications
    c.drawString(100, 750, "===== PAGE 2 =====")
    c.drawString(100, 720, "CERTIFICATIONS AND ORIGIN:")
    c.drawString(100, 700, "Country of Origin: Germany")
    c.drawString(100, 680, "Vegan Status: Vegan certified")
    c.drawString(100, 660, "Halal Status: Halal certified (expires 2025-06-30)")
    c.drawString(100, 640, "Organic Status: Not organic")
    c.drawString(100, 620, "GMO Status: GMO-free certified")
    c.drawString(100, 600, "")
    c.drawString(100, 580, "TECHNICAL DATA:")
    c.drawString(100, 560, "Composition: 70% Cetearyl Alcohol, 30% Cetearyl Glucoside")
    c.drawString(100, 540, "Certificate of Analysis: Batch COA-2024-001")
    c.drawString(100, 520, "Manufacturing Date: 2024-01-15")
    c.drawString(100, 500, "Shelf Life: 36 months")
    c.drawString(100, 480, "Storage: Store in cool, dry place")
    
    c.save()
    print(f"Created comprehensive test PDF: {filename}")


def main():
    create_cosmetics_test_pdf()
    create_food_grade_test_pdf() 
    create_comprehensive_test_pdf()
    print("\nAll test PDFs created successfully!")
    print("Use these with different schemas to test the modular system:")
    print("  python config_extractor.py schemas/cosmetics_basic.json test_cosmetics.pdf")
    print("  python config_extractor.py schemas/food_grade.json test_food_grade.pdf")
    print("  python config_extractor.py schemas/raw_materials.json test_comprehensive.pdf")


if __name__ == "__main__":
    main()