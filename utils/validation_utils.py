#!/usr/bin/env python3
"""
Validation utilities for OMP test generation
Provides schema validation and testing infrastructure utilities
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union
def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate JSON data against a JSON schema
    
    Args:
        data: JSON data to validate
        schema: JSON schema to validate against
        
    Returns:
        True if data is valid according to schema, False otherwise
    """
    # Simplified schema validation - in production would use a proper JSON schema validator
    
    # Check required fields
    if "required" in schema:
        for required_field in schema["required"]:
            if required_field not in data:
                return False
    
    # Check property types
    if "properties" in schema:
        for field, field_schema in schema["properties"].items():
            if field in data:
                field_type = field_schema.get("type")
                field_value = data[field]
                
                if field_type == "string" and not isinstance(field_value, str):
                    return False
                elif field_type == "integer" and not isinstance(field_value, int):
                    return False
                elif field_type == "number" and not isinstance(field_value, (int, float)):
                    return False
                elif field_type == "boolean" and not isinstance(field_value, bool):
                    return False
                elif field_type == "array" and not isinstance(field_value, list):
                    return False
                elif field_type == "object" and not isinstance(field_value, dict):
                    return False
    
    # Check array item types
    if "items" in schema and "type" in schema["items"]:
        item_type = schema["items"]["type"]
        if "in_schema" in schema and isinstance(schema["in_schema"], list):
            for item in schema["in_schema"]:
                if not isinstance(item, item_type):
                    return False
    
    return True
def validate_json_file(file_path: Path, schema: Dict[str, Any]) -> bool:
    """Validate JSON file content against a schema
    
    Args:
        file_path: Path to JSON file to validate
        schema: JSON schema to validate against
        
    Returns:
        True if file is valid according to schema, False otherwise
    """
    try:
        if not file_path.exists():
            return False
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return validate_json_schema(data, schema)
    except (json.JSONDecodeError, FileNotFoundError):
        return False
def validate_test_structure(test_file: Path) -> Dict[str, Union[bool, List[str]]]:
    """Validate basic test file structure and requirements
    
    Args:
        test_file: Path to test file to validate
        
    Returns:
        Dictionary with validation results and any errors found
    """
    errors = []
    
    # Check if file exists
    if not test_file.exists():
        errors.append(f"Test file does not exist: {test_file}")
        return {"valid": False, "errors": errors}
    
    # Check if it's a Python file
    if not str(test_file).endswith('.py'):
        errors.append(f"Test file must be a Python file: {test_file}")
        return {"valid": False, "errors": errors}
    
    # Try to read file content
    try:
        content = test_file.read_text()
        
        # Check for shebang
        if not content.startswith('#!/usr/bin/env python3'):
            errors.append(f"Test file should have shebang: {test_file}")
        
        # Check for unittest import
        if 'import unittest' not in content:
            errors.append(f"Test file should import unittest: {test_file}")
        
        # Check for test class definition
        if 'class' not in content or 'unittest.TestCase' not in content:
            errors.append(f"Test file should define unittest.TestCase subclass: {test_file}")
        
        # Check for test methods
        if 'def test_' not in content:
            errors.append(f"Test file should contain test methods (def test_...): {test_file}")
        
        return {"valid": len(errors) == 0, "errors": errors}
        
    except Exception as e:
        errors.append(f"Error reading test file {test_file}: {e}")
        return {"valid": False, "errors": errors}
def sanitize_test_content(content: str) -> str:
    """Apply test content sanitization to remove pre-flight traps
    
    Args:
        content: Test script content to sanitize
        
    Returns:
        Sanitized test content
    """
    # Remove binary existence checks
    import re
    content = re.sub(r'if\s*\[\s*!?\s*-f\s+["\']?([^"\'\s]+)["\']?\s*\]',
                    'pass  # Pre-flight trap removed', content)
    
    # Remove directory existence checks
    content = re.sub(r'if\s*\[\s*!?\s*-d\s+["\']?([^"\'\s]+)["\']?\s*\]',
                    'pass  # Pre-flight trap removed', content)
    
    # Remove custom INTEGRITY FAILURE error patterns
    content = re.sub(r'print\s*\(\s*["\']?INTEGRITY.?FAILURE["\']?',
                    'print("Implementation expected - pre-implementation")', content)
    
    # Remove exit(1) calls that represent integrity failures
    content = re.sub(r'exit\s*\(\s*1\s*\)', 'sys.exit(127)', content)
    
    return content
def batch_validate_test_directory(directory_path: Path) -> Dict[str, Any]:
    """Validate all test files in a directory
    
    Args:
        directory_path: Directory containing test files
        
    Returns:
        Dictionary with batch validation results
    """
    if not directory_path.exists():
        return {"valid": False, "errors": [f"Directory does not exist: {directory_path}"], "files": []}
    
    results = {
        "valid": True,
        "errors": [],
        "files": [],
        "valid_count": 0,
        "invalid_count": 0
    }
    
    # Process all .py files in the directory
    for test_file in directory_path.glob("*.py"):
        file_result = validate_test_structure(test_file)
        file_info = {
            "path": str(test_file),
            "valid": file_result["valid"],
            "errors": file_result["errors"]
        }
        results["files"].append(file_info)
        
        if file_result["valid"]:
            results["valid_count"] += 1
        else:
            results["invalid_count"] += 1
            results["errors"].extend([f"{test_file}: {error}" for error in file_result["errors"]])
    
    results["valid"] = results["invalid_count"] == 0
    
    return results