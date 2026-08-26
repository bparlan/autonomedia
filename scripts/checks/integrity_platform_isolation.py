#!/usr/bin/env python3
"""
Implements FR-INTEGRITY_PLATFORM_ISOLATION: Validates cross-platform isolation boundaries.

This script analyzes imports between platform adapters (src/autonomedia/platforms/) 
to ensure proper isolation between different platform modules.
"""

import os
import sys
import json
import argparse
import ast
from pathlib import Path
from datetime import datetime

# Custom exception for import violations
class CrossPlatformImportViolation(Exception):
    """Raised when cross-platform imports detected."""
    def __init__(self, message, import_path):
        super().__init__(message)
        self.import_path = import_path

# Script implementation flag
FR_INTEGRITY_PLATFORM_ISOLATION = True

# Platform adapters paths
PLATFORM_PATHS = [
    "src/autonomedia/platforms/",
]


def analyze_platform_isolation(root_dir: str = "."):
    """Analyze cross-platform isolation boundaries."""
    validation_results = {
        "fully_isolated_platforms": [],
        "cross_platform_violations": [],
        "isolation_score": 100.0,
        "generated_at": datetime.now().isoformat() + "Z"
    }
    
    root_path = Path(root_dir)
    
    # Find all platform adapter files
    platform_files = []
    for pattern in PLATFORM_PATHS:
        platform_files.extend(root_path.glob(f"{pattern}*.py"))
        platform_files.extend(root_path.glob(f"{pattern}*/**/*.py"))
    
    # Organize files by platform directory
    platform_to_files = {}
    for platform_file in platform_files:
        # Determine platform directory
        platform_dir = None
        for pattern in PLATFORM_PATHS:
            if str(platform_file).startswith(pattern):
                platform_dir = pattern.rstrip("/")
                break
        
        if platform_dir:
            if platform_dir not in platform_to_files:
                platform_to_files[platform_dir] = []
            platform_to_files[platform_dir].append(platform_file)
    
    # Analyze each platform's files for cross-platform imports
    all_platforms_fully_isolated = True
    
    for platform_dir, platform_files_list in platform_to_files.items():
        platform_name = platform_dir.split("/")[-1]
        is_fully_isolated = True
        
        for platform_file in platform_files_list:
            try:
                with open(platform_file, "r") as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if _is_cross_platform_import(alias.name, platform_dir, root_path):
                                violation = {
                                    "type": "CROSS_PLATFORM_IMPORT",
                                    "file": str(platform_file),
                                    "import_path": alias.name,
                                    "violating_platform": platform_name,
                                    "message": f"Platform {platform_name} file {platform_file} imports from another platform: {alias.name}"
                                }
                                validation_results["cross_platform_violations"].append(violation)
                                is_fully_isolated = False
                                validation_results["isolation_score"] -= 20.0
                                
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            if _is_cross_platform_import(node.module, platform_dir, root_path):
                                violation = {
                                    "type": "CROSS_PLATFORM_IMPORT",
                                    "file": str(platform_file),
                                    "import_path": f"from {node.module}",
                                    "violating_platform": platform_name,
                                    "message": f"Platform {platform_name} file {platform_file} imports from another platform: from {node.module}"
                                }
                                validation_results["cross_platform_violations"].append(violation)
                                is_fully_isolated = False
                                validation_results["isolation_score"] -= 20.0
                
            except Exception as e:
                violation = {
                    "type": "ANALYSIS_ERROR",
                    "file": str(platform_file),
                    "import_path": "",
                    "violating_platform": platform_name,
                    "message": f"Error analyzing file {platform_file}: {str(e)}"
                }
                validation_results["cross_platform_violations"].append(violation)
                is_fully_isolated = False
                validation_results["isolation_score"] -= 10.0
        
        if is_fully_isolated:
            validation_results["fully_isolated_platforms"].append(platform_name)
    
    # Ensure isolation score doesn't go below 0
    validation_results["isolation_score"] = max(0.0, validation_results["isolation_score"])
    
    # Update overall isolation status
    if len(validation_results["cross_platform_violations"]) > 0:
        all_platforms_fully_isolated = False
    
    return validation_results


def _is_cross_platform_import(import_path: str, source_platform_dir: str, root_path: Path) -> bool:
    """Check if import path is from a different platform."""
    # Check if it's a platform import
    for pattern in PLATFORM_PATHS:
        normalized = import_path.replace(".", "/")
        if normalized.startswith(pattern.rstrip("/")):
            # Check if it's from the same platform
            source_platform_normalized = source_platform_dir.replace("/", ".") + "."
            if normalized.startswith(source_platform_normalized) or import_path.startswith(source_platform_dir.replace("/", ".") + "."):
                return False
            else:
                return True
    return False


def validate_output_schema(report):
    """Validate output schema for platform isolation report."""
    required_keys = ["fully_isolated_platforms", "cross_platform_violations", "isolation_score", "generated_at"]
    
    for key in required_keys:
        if key not in report:
            raise ValueError(f"Required key '{key}' missing from report")
    
    if not isinstance(report["fully_isolated_platforms"], list):
        raise ValueError("fully_isolated_platforms must be a list")
    
    if not isinstance(report["cross_platform_violations"], list):
        raise ValueError("cross_platform_violations must be a list")
    
    if not isinstance(report["isolation_score"], (int, float)):
        raise ValueError("isolation_score must be a number")
    
    if not 0 <= report["isolation_score"] <= 100:
        raise ValueError("isolation_score must be between 0 and 100")
    
    # Validate each violation has required fields
    for violation in report["cross_platform_violations"]:
        required_violation_fields = ["type", "file", "import_path", "violating_platform", "message"]
        for field in required_violation_fields:
            if field not in violation:
                raise ValueError(f"Violation missing required field: {field}")


def write_report(report, output_path):
    """Write validation report to file."""
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)


def main():
    """Main entry point for platform isolation validation script."""
    parser = argparse.ArgumentParser(description="Validate cross-platform isolation boundaries")
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
        validation_results = analyze_platform_isolation()
        
        # Validate output schema
        validate_output_schema(validation_results)
        
        # Write report
        write_report(validation_results, args.output)
        
        print(f"Validation completed. Report written to {args.output}")
        print(f"Isolation score: {validation_results['isolation_score']}")
        print(f"Fully isolated platforms: {len(validation_results['fully_isolated_platforms'])}")
        print(f"Cross-platform violations found: {len(validation_results['cross_platform_violations'])}")
        
        # Exit with error code if violations found
        if validation_results["isolation_score"] < 100.0:
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())