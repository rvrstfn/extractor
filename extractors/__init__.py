"""
Modular document extraction system
"""

from .base_extractor import BaseExtractor
from .schema_extractor import SchemaExtractor

__all__ = ['BaseExtractor', 'SchemaExtractor']