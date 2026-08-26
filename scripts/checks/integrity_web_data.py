#!/usr/bin/env python3
"""
Implements FR-INTEGRITY_WEB_DATA_BINDING: Validates web application ↔ data registry integration boundaries.

This script analyzes imports between web application (src/web/templates/) and 
data registry (storage/data/) to ensure proper integration boundaries are maintained.
"""

import os
import sys
import json
import argparse
import ast
from pathlib import Path
from datetime import datetime

# Custom exception for import violations
class WebDataRegistryViolation(Exception):
    """Raised when web application imports from data registry."""
    def __init__(self, message, import_path):
        super().__init__(message)
        self.import_path = import_path

# Script implementation flag
FR_INTEGRITY_WEB_DATA_BINDING = True

# Web application paths
WEB_APP_PATHS = [
    "src/web/templates/",
    "src/web/",
]

# Data registry paths
DATA_REGISTRY_PATHS = [
    "storage/data/",
]


def analyze_web_data_integration(root_dir: str = "."):
    """Analyze web application ↔ data registry integration boundaries."""
    validation_results = {
        "validated_bindings": [],
        "violations": [],
        "valid_access": True,
        "generated_at": datetime.now().isoformat() + "Z"
    }
    
    root_path = Path(root_dir)
    
    # Find all Python files in web application
    web_files = []
    for pattern in WEB_APP_PATHS:
        web_files.extend(root_path.glob(f"{pattern}*.py"))
        web_files.extend(root_path.glob(f"{pattern}*/**/*.py"))
    
    # Find all Python files in data registry
    data_files = []
    for pattern in DATA_REGISTRY_PATHS:
        data_files.extend(root_path.glob(f"{pattern}*.py"))
        data_files.extend(root_path.glob(f"{pattern}*/**/*.py"))
    
    # Analyze web application files for data registry imports (violations)
    for web_file in web_files:
        try:
            with open(web_file, "r") as f:
                content = f.read()
                tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_data_registry_import(alias.name):
                            violation = {
                                "type": "WEB_IMPORTS_FROM_DATA_REGISTRY",
                                "file": str(web_file),
                                "import_path": alias.name,
                                "message": f"Web application file {web_file} imports from data registry: {alias.name}"
                            }
                            validation_results["violations"].append(violation)
                            validation_results["valid_access"] = False
                            
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        if _is_data_registry_import(node.module):
                            violation = {
                                "type": "WEB_IMPORTS_FROM_DATA_REGISTRY",
                                "file": str(web_file),
                                "import_path": f"from {node.module}",
                                "message": f"Web application file {web_file} imports from data registry: from {node.module}"
                            }
                            validation_results["violations"].append(violation)
                            validation_results["valid_access"] = False
            
            # Record valid binding
            binding = {
                "from": str(web_file),
                "to": "web_application",
                "valid": True,
                "binding_type": "web_application"
            }
            validation_results["validated_bindings"].append(binding)
            
        except Exception as e:
            violation = {
                "type": "ANALYSIS_ERROR",
                "file": str(web_file),
                "import_path": "",
                "message": f"Error analyzing file {web_file}: {str(e)}"
            }
            validation_results["violations"].append(violation)
            validation_results["valid_access"] = False
    
    # Analyze data registry files for web application imports (should be valid)
    for data_file in data_files:
        try:
            with open(data_file, "r") as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Record binding - data registry to web application is valid integration
            binding = {
                "from": str(data_file),
                "to": "data_registry",
                "valid": True,
                "binding_type": "data_registry_to_web"
            }
            validation_results["validated_bindings"].append(binding)
            
        except Exception as e:
            violation = {
                "type": "ANALYSIS_ERROR",
                "file": str(data_file),
                "import_path": "",
                "message": f"Error analyzing file {data_file}: {str(e)}"
            }
            validation_results["violations"].append(violation)
            validation_results["valid_access"] = False
    
    return validation_results


def _is_data_registry_import(import_path: str) -> bool:
    """Check if import path is from data registry."""
    normalized = import_path.replace(".", "/")
    return any(
        normalized.startswith(pattern.rstrip("/")) or 
        import_path.startswith(pattern.replace("/", "."))
        for pattern in DATA_REGISTRY_PATHS
    )


def validate_output_schema(report):
    """Validate output schema for web-data integration report."""
    required_keys = ["validated_bindings", "violations", "valid_access", "generated_at"]
    
    for key in required_keys:
        if key not in report:
            raise ValueError(f"Required key '{key}' missing from report")
    
    if not isinstance(report["validated_bindings"], list):
        raise ValueError("validated_bindings must be a list")
    
    if not isinstance(report["violations"], list):
        raise ValueError("violations must be a list")
    
    if not isinstance(report["valid_access"], bool):
        raise ValueError("valid_access must be a boolean")
    
    # Validate each binding has required fields
    for binding in report["validated_bindings"]:
        required_binding_fields = ["from", "to", "valid", "binding_type"]
        for field in required_binding_fields:
            if field not in binding:
                raise ValueError(f"Binding missing required field: {field}")
    
    # Validate each violation has required fields
    for violation in report["violations"]:
        required_violation_fields = ["type", "file", "import_path", "message"]
        for field in required_violation_fields:
            if field not in violation:
                raise ValueError(f"Violation missing required field: {field}")


def write_report(report, output_path):
    """Write validation report to file."""
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)


def main():
    """Main entry point for web-data integration validation script."""
    parser = argparse.ArgumentParser(description="Validate web application ↔ data registry integration boundaries")
    parser.add_argument("--validate", action="store_true", help="Run validation and generate report")
    parser.add_argument("--output", help="Output file path for validation report")
    
    args = parser.parse_args()
    
    if not args.validate:
        print("Use --validate flag to run validation")
        return 1
    
    if not args.output:
        print("Use --output flag to specify output file")
        return 1
    
    try:
        # Run validation analysis
        validation_results = analyze_web_data_integration()
        
        # Validate output schema
        validate_output_schema(validation_results)
        
        # Write report
        write_report(validation_results, args.output)
        
        print(f"Validation completed. Report written to {args.output}")
        print(f"Valid access: {validation_results['valid_access']}")
        print(f"Total bindings analyzed: {len(validation_results['validated_bindings']) + len(validation_results['violations'])}")
        print(f"Violations found: {len(validation_results['violations'])}")
        
        # Exit with error code if violations found
        if not validation_results["valid_access"]:
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())