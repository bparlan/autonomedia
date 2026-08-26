#!/usr/bin/env python3
"""
Implements FR-INTEGRITY_RUNTIME_DETERMINISM: Validates runtime determinism across integration binding validation.

This script runs the integration binding validation multiple times and compares the outputs
to ensure deterministic behavior. It generates binding matrices and performs determinism checks.
"""

import os
import sys
import json
import argparse
import hashlib
import ast
from pathlib import Path
from datetime import datetime

# Custom exception for determinism violations
class DeterminismViolation(Exception):
    """Raised when determinism checks fail."""
    def __init__(self, message, checksum_diff):
        super().__init__(message)
        self.checksum_diff = checksum_diff

# Script implementation flag
FR_INTEGRITY_RUNTIME_DETERMINISM = True

# Integration binding validation scripts
INTEGRATION_SCRIPTS = [
    "scripts/checks/integrity_core_ai.py",
    "scripts/checks/integrity_platform_core.py",
    "scripts/checks/integrity_web_data.py",
    "scripts/checks/integrity_platform_isolation.py"
]


def get_file_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    if not os.path.exists(file_path):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_integration_validation(script_path, output_file):
    """Run a single integration validation script."""
    cmd = ["uv", "run", "python", script_path, "--validate", "--output", output_file]
    
    # Set environment variable for repository root
    env = os.environ.copy()
    env["REPO_ROOT"] = "."
    
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        env=env
    )
    
    return result


def generate_binding_matrix():
    """Generate a binding matrix by running all integration validation scripts."""
    binding_matrix = {
        "validation_round": datetime.now().isoformat() + "Z",
        "scripts_executed": [],
        "binding_results": {},
        "generated_at": datetime.now().isoformat() + "Z"
    }
    
    for script_path in INTEGRATION_SCRIPTS:
        if os.path.exists(script_path):
            # Generate output file name based on script
            script_name = os.path.basename(script_path).replace('.py', '')
            output_file = f"storage/data/integration_{script_name}_binding.json"
            
            # Run the validation script
            result = run_integration_validation(script_path, output_file)
            
            binding_matrix["scripts_executed"].append({
                "script": script_path,
                "output_file": output_file,
                "exit_code": result.returncode,
                "success": result.returncode == 0
            })
            
            # Read the generated report for binding results
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, "r") as f:
                    report_data = json.load(f)
                
                binding_matrix["binding_results"][script_name] = {
                    "exit_code": result.returncode,
                    "binding_count": len(report_data.get("validated_bindings", [])),
                    "violation_count": len(report_data.get("violations", [])),
                    "isolation_score": report_data.get("isolation_score", 100.0),
                    "valid_access": report_data.get("valid_access", True),
                    "output_file": output_file,
                    "checksum": get_file_checksum(output_file)
                }
            else:
                binding_matrix["binding_results"][script_name] = {
                    "exit_code": result.returncode,
                    "error": result.stderr,
                    "output_file": output_file,
                    "checksum": None
                }
        else:
            binding_matrix["scripts_executed"].append({
                "script": script_path,
                "output_file": None,
                "exit_code": 127,
                "success": False,
                "error": "Script not found"
            })
            
            binding_matrix["binding_results"][os.path.basename(script_path).replace('.py', '')] = {
                "exit_code": 127,
                "error": "Script not found",
                "output_file": None,
                "checksum": None
            }
    
    return binding_matrix


def compare_matrices(matrix_file1, matrix_file2):
    """Compare two binding matrices for determinism."""
    determinism_result = {
        "checksum_match": False,
        "determinism_compliant": False,
        "matrix1_path": matrix_file1,
        "matrix2_path": matrix_file2,
        "comparison_time": datetime.now().isoformat() + "Z",
        "differences": []
    }
    
    # Calculate checksums
    checksum1 = get_file_checksum(matrix_file1)
    checksum2 = get_file_checksum(matrix_file2)
    
    determinism_result["checksum1"] = checksum1
    determinism_result["checksum2"] = checksum2
    
    if checksum1 and checksum2:
        determinism_result["checksum_match"] = (checksum1 == checksum2)
    
    if determinism_result["checksum_match"]:
        determinism_result["determinism_compliant"] = True
    
    # Load and compare matrices for detailed differences
    try:
        with open(matrix_file1, "r") as f:
            matrix1_data = json.load(f)
        
        with open(matrix_file2, "r") as f:
            matrix2_data = json.load(f)
        
        # Compare key fields
        if "validation_round" in matrix1_data and "validation_round" in matrix2_data:
            determinism_result["differences"].append({
                "field": "validation_round",
                "matrix1": matrix1_data["validation_round"],
                "matrix2": matrix2_data["validation_round"]
            })
        
        # Compare binding results
        if "binding_results" in matrix1_data and "binding_results" in matrix2_data:
            matrix1_bindings = matrix1_data["binding_results"]
            matrix2_bindings = matrix2_data["binding_results"]
            
            for script_name in set(list(matrix1_bindings.keys()) + list(matrix2_bindings.keys())):
                if script_name in matrix1_bindings and script_name in matrix2_bindings:
                    script1_data = matrix1_bindings[script_name]
                    script2_data = matrix2_bindings[script_name]
                    
                    if script1_data.get("checksum") != script2_data.get("checksum"):
                        determinism_result["differences"].append({
                            "field": f"binding_results.{script_name}.checksum",
                            "matrix1": script1_data.get("checksum"),
                            "matrix2": script2_data.get("checksum")
                        })
    
    except Exception as e:
        determinism_result["error"] = f"Error comparing matrices: {str(e)}"
    
    return determinism_result


def validate_output_schema(report, report_type="binding_matrix"):
    """Validate output schema for binding matrix or determinism report."""
    if report_type == "binding_matrix":
        required_keys = ["validation_round", "scripts_executed", "binding_results", "generated_at"]
        
        for key in required_keys:
            if key not in report:
                raise ValueError(f"Required key '{key}' missing from binding matrix")
        
        if not isinstance(report["scripts_executed"], list):
            raise ValueError("scripts_executed must be a list")
        
        if not isinstance(report["binding_results"], dict):
            raise ValueError("binding_results must be a dict")
        
        for script_name, script_data in report["binding_results"].items():
            if not isinstance(script_data, dict):
                raise ValueError(f"binding_results[{script_name}] must be a dict")
            
            if "exit_code" not in script_data:
                raise ValueError(f"binding_results[{script_name}] missing exit_code")
            
            if script_data.get("exit_code") == 0 and "binding_count" in script_data:
                if not isinstance(script_data["binding_count"], int):
                    raise ValueError(f"binding_results[{script_name}].binding_count must be an integer")
    
    elif report_type == "determinism_report":
        required_keys = ["checksum_match", "determinism_compliant", "matrix1_path", "matrix2_path", "comparison_time"]
        
        for key in required_keys:
            if key not in report:
                raise ValueError(f"Required key '{key}' missing from determinism report")
        
        if not isinstance(report["checksum_match"], bool):
            raise ValueError("checksum_match must be a boolean")
        
        if not isinstance(report["determinism_compliant"], bool):
            raise ValueError("determinism_compliant must be a boolean")


def write_report(report, output_path):
    """Write validation report to file."""
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)


def main():
    """Main entry point for runtime determinism validation script."""
    parser = argparse.ArgumentParser(description="Validate runtime determinism of integration binding validation")
    parser.add_argument("--validate", action="store_true", help="Run validation and generate binding matrix")
    parser.add_argument("--output", help="Output file path for binding matrix")
    parser.add_argument("--compare", nargs=2, metavar=("MATRIX1", "MATRIX2"), help="Compare two binding matrices")
    
    args = parser.parse_args()
    
    if args.compare:
        # Compare mode
        if len(args.compare) != 2:
            print("Error: --compare requires exactly two matrix files")
            return 1
        
        matrix_file1, matrix_file2 = args.compare
        
        try:
            # Compare matrices
            determinism_result = compare_matrices(matrix_file1, matrix_file2)
            
            # Validate output schema
            validate_output_schema(determinism_result, "determinism_report")
            
            # Write report
            if not args.output:
                args.output = "storage/data/integration_determinism_report.json"
            
            write_report(determinism_result, args.output)
            
            print(f"Determinism comparison completed. Report written to {args.output}")
            print(f"Checksum match: {determinism_result['checksum_match']}")
            print(f"Determinism compliant: {determinism_result['determinism_compliant']}")
            
            # Exit with error code if not deterministic
            if not determinism_result["determinism_compliant"]:
                return 1
            
            return 0
            
        except Exception as e:
            print(f"Determinism comparison failed: {str(e)}")
            return 1
    
    elif args.validate and args.output:
        # Validation mode
        try:
            # Generate binding matrix
            binding_matrix = generate_binding_matrix()
            
            # Validate output schema
            validate_output_schema(binding_matrix, "binding_matrix")
            
            # Write report
            write_report(binding_matrix, args.output)
            
            print(f"Binding matrix generated. Report written to {args.output}")
            print(f"Validation round: {binding_matrix['validation_round']}")
            print(f"Scripts executed: {len(binding_matrix['scripts_executed'])}")
            
            return 0
            
        except Exception as e:
            print(f"Binding matrix generation failed: {str(e)}")
            return 1
    
    else:
        print("Use either:")
        print("  --validate --output <file>    Generate binding matrix")
        print("  --compare <matrix1> <matrix2>  Compare two binding matrices")
        return 1


if __name__ == "__main__":
    # Import subprocess here to avoid issues in some environments
    import subprocess
    sys.exit(main())