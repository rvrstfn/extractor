#!/usr/bin/env python3
"""
Create a tiny test PDF with raw material information
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf():
    filename = "test_material.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add some test content that matches our extraction requirements
    c.drawString(100, 750, "Material Safety Data Sheet")
    c.drawString(100, 730, "Product Name: Glycerin USP")
    c.drawString(100, 710, "CAS Number: 56-81-5")
    c.drawString(100, 690, "REACH Registration: 01-2119471987-18-0000")
    c.drawString(100, 670, "Heavy Metals: <10ppm lead")
    c.drawString(100, 650, "Country of Origin: USA")
    c.drawString(100, 630, "GMO Status: GMO-free certified")
    
    c.save()
    print(f"Created test PDF: {filename}")

if __name__ == "__main__":
    create_test_pdf()