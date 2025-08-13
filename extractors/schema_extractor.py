#!/usr/bin/env python3
"""
Schema-based extractor that loads configurations from JSON files
"""

import json
from pathlib import Path
from typing import Dict, Any

from .base_extractor import BaseExtractor


class SchemaExtractor(BaseExtractor):
    """Extractor that loads schema from JSON configuration files"""
    
    def __init__(self, schema_file: str = None, model_id: str = "gemma3", model_url: str = "http://localhost:11434"):
        super().__init__(model_id, model_url)
        if schema_file:
            self.load_schema(schema_file)
    
    def load_schema(self, schema_file: str) -> Dict[str, Any]:
        """Load extraction schema from JSON file"""
        schema_path = Path(schema_file)
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            # Validate schema structure
            self._validate_schema()
            
            # Create examples from schema
            self.examples = self.create_examples_from_schema()
            
            return self.schema
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file {schema_file}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading schema from {schema_file}: {e}")
    
    def _validate_schema(self):
        """Validate that schema has required fields"""
        required_fields = ['name', 'description', 'categories']
        
        for field in required_fields:
            if field not in self.schema:
                raise ValueError(f"Schema missing required field: {field}")
        
        # Validate categories structure
        categories = self.schema['categories']
        if not isinstance(categories, dict):
            raise ValueError("Schema 'categories' must be a dictionary")
        
        for category_name, category_items in categories.items():
            if not isinstance(category_items, dict):
                raise ValueError(f"Category '{category_name}' must contain dictionary of items")
            
            for item_name, item_config in category_items.items():
                if 'description' not in item_config:
                    raise ValueError(f"Item '{category_name}.{item_name}' missing description")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema metadata"""
        if not self.schema:
            return {}
        
        return {
            'name': self.schema.get('name', ''),
            'description': self.schema.get('description', ''),
            'categories': list(self.schema.get('categories', {}).keys()),
            'total_requirements': sum(
                len(items) for items in self.schema.get('categories', {}).values()
            )
        }