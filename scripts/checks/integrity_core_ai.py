#!/usr/bin/env python3
"""
Core AI Integration Binding Validation Script

Implements FR-INTEGRITY_CORE_AI_BINDING: Validates Core Infrastructure ↔ AI Engine integration boundaries.

Produces: storage/data/integration_core_ai_binding.json

Exit codes:
0: Success - all core-AI integrations valid
2: Cross-layer imports detected
3: Analysis failed
"""

import json
import argparse
import ast
import sys
from datetime import datetime
from pathlib import Path

# Custom exception for import violations
class CoreAIImportViolation(Exception):
    """Raised when core infrastructure imports from AI engine."""
    def __init__(self, message: str, import_path: str):
        super().__init__(message)
        self.import_path = import_path

# Script implementation flag
FR_INTEGRITY_CORE_AI_BINDING = True

# Core infrastructure paths
CORE_INFRASTRUCTURE_PATHS = [
    "src/autonomedia/core/",
    "src/autonomedia/database/",
    "src/autonomedia/content/",
]

# AI engine paths
AI_ENGINE_PATHS = [
    "src/autonomedia/ai/rewriting/",
]

def validate_core_ai_integrity(repo_root: str = ".") -> dict:
    """Validate Core ↔ AI Engine integration boundaries.
    
    Args:
        repo_root: Repository root path
        
    Returns:
        Dict with validated_bindings, violations, total_bindings, and generated_at
    """
    repo_path = Path(repo_root).resolve()
    validated_bindings = []
    violations = []
    total_bindings = 0
    
    # Scan for imports in core infrastructure that reference AI
    for py_file in repo_path.rglob("*.py"):
        # Skip AI files themselves
        if any(ai_path in str(py_file) for ai_path in AI_ENGINE_PATHS):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_ai_import(alias.name):
                            violations.append({
                                "from_module": str(py_file.relative_to(repo_path)),
                                "to_module": alias.name,
                                "violation_type": "cross_layer_import",
                                "severity": "HIGH"
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module and _is_ai_import(node.module):
                        violations.append({
                            "from_module": str(py_file.relative_to(repo_path)),
                            "to_module": node.module,
                            "violation_type": "cross_layer_import",
                            "severity": "HIGH"
                        })
                        
        except (SyntaxError, UnicodeDecodeError, PermissionError, OSError):
            continue
    
    # Scan for imports in AI engine that reference core (should be allowed based on spec)
    for py_file in repo_path.rglob("*.py"):
        if any(ai_path in str(py_file) for ai_path in AI_ENGINE_PATHS):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if _is_core_import(alias.name):
                                # This is a valid binding from AI to core
                                validated_bindings.append({
                                    "from_module": str(py_file.relative_to(repo_path)),
                                    "to_module": alias.name,
                                    "binding_type": "interface",
                                    "valid": True
                                })
                                total_bindings += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and _is_core_import(node.module):
                            validated_bindings.append({
                                "from_module": str(py_file.relative_to(repo_path)),
                                "to_module": node.module,
                                "binding_type": "interface",
                                "valid": True
                            })
                            total_bindings += 1
                            
            except (SyntaxError, UnicodeDecodeError, PermissionError, OSError):
                continue
    
    return {
        "validated_bindings": validated_bindings,
        "violations": violations,
        "total_bindings": total_bindings,
        "generated_at": datetime.now().isoformat()
    }

def analyze_integration_bindings(root_dir: str = ".") -> dict:
    """Analyze integration bindings between all layers (simplified for this implementation).
    
    Args:
        root_dir: Repository root path
        
    Returns:
        Dict with integration binding matrix
    """
    repo_path = Path(root_dir).resolve()
    
    # For this implementation, we'll return a simplified binding matrix
    binding_matrix = {
        "core_to_ai": [],
        "ai_to_core": [],
        "platform_to_core": [],
        "core_to_platform": [],
        "web_to_data": [],
        "data_to_web": []
    }
    
    # Analyze core to AI bindings
    core_to_ai = []
    for py_file in repo_path.rglob("*.py"):
        if any(core_path in str(py_file) for core_path in CORE_INFRASTRUCTURE_PATHS):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if _is_ai_import(alias.name):
                                core_to_ai.append({
                                    "from_module": str(py_file.relative_to(repo_path)),
                                    "to_module": alias.name,
                                    "binding_type": "runtime"
                                })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and _is_ai_import(node.module):
                            core_to_ai.append({
                                "from_module": str(py_file.relative_to(repo_path)),
                                "to_module": node.module,
                                "binding_type": "runtime"
                            })
            except (SyntaxError, UnicodeDecodeError, PermissionError, OSError):
                continue
    
    binding_matrix["core_to_ai"] = core_to_ai
    
    # Analyze AI to core bindings (allowed per spec)
    ai_to_core = []
    for py_file in repo_path.rglob("*.py"):
        if any(ai_path in str(py_file) for ai_path in AI_ENGINE_PATHS):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if _is_core_import(alias.name):
                                ai_to_core.append({
                                    "from_module": str(py_file.relative_to(repo_path)),
                                    "to_module": alias.name,
                                    "binding_type": "interface"
                                })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and _is_core_import(node.module):
                            ai_to_core.append({
                                "from_module": str(py_file.relative_to(repo_path)),
                                "to_module": node.module,
                                "binding_type": "interface"
                            })
            except (SyntaxError, UnicodeDecodeError, PermissionError, OSError):
                continue
    
    binding_matrix["ai_to_core"] = ai_to_core
    
    return binding_matrix

def write_integration_report(report: dict, output_path: str) -> None:
    """Write integration report to file.
    
    Args:
        report: Integration report dictionary
        output_path: Output file path
    """
    try:
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
            
    except OSError as e:
        print(f"Error writing report to {output_path}: {e}")
        raise

def _is_ai_import(import_path: str) -> bool:
    """Check if import path is from AI engine."""
    normalized = import_path.replace(".", "/")
    return any(
        normalized.startswith(pattern.rstrip("/")) or
        import_path.startswith(pattern.replace("/", "."))
        for pattern in AI_ENGINE_PATHS
    )

def _is_core_import(import_path: str) -> bool:
    """Check if import path is from core infrastructure."""
    normalized = import_path.replace(".", "/")
    return any(
        normalized.startswith(pattern.rstrip("/")) or
        import_path.startswith(pattern.replace("/", "."))
        for pattern in CORE_INFRASTRUCTURE_PATHS
    )

def validate_output_schema(report: dict) -> None:
    """Validate output schema for integration binding report."""
    required_keys = ["validated_bindings", "violations", "total_bindings", "generated_at"]

    for key in required_keys:
        if key not in report:
            raise ValueError(f"Required key '{key}' missing from report")

    if not isinstance(report["validated_bindings"], list):
        raise ValueError("validated_bindings must be a list")

    if not isinstance(report["violations"], list):
        raise ValueError("violations must be a list")

    if not isinstance(report["total_bindings"], int):
        raise ValueError("total_bindings must be an integer")

    # Validate each binding has required fields
    for binding in report["validated_bindings"]:
        required_binding_fields = ["from_module", "to_module", "binding_type", "valid"]
        for field in required_binding_fields:
            if field not in binding:
                raise ValueError(f"Binding missing required field: {field}")

    # Validate each violation has required fields
    for violation in report["violations"]:
        required_violation_fields = ["from_module", "to_module", "violation_type", "severity"]
        for field in required_violation_fields:
            if field not in violation:
                raise ValueError(f"Violation missing required field: {field}")

def main() -> int:
    """Main entry point for core AI integration validation script."""
    parser = argparse.ArgumentParser(description="Core AI Integration Binding Validation")
    parser.add_argument("--validate", "-v", action="store_true", help="Validate integration boundaries")
    parser.add_argument("--output", "-o", default="storage/data/integration_core_ai_binding.json", help="Output report path")
    
    args = parser.parse_args()

    try:
        if args.validate:
            # Validate core-AI integration
            report = validate_core_ai_integrity()
            
            # Analyze integration bindings
            binding_matrix = analyze_integration_bindings()
            
            # Write reports
            write_integration_report(report, args.output)
            
            # Write binding matrix for runtime determinism
            binding_matrix_path = "storage/data/integration_binding_matrix_1.json"
            write_integration_report(binding_matrix, binding_matrix_path)
            
            # Validate output schema
            validate_output_schema(report)
            
            # Check for violations
            if report["violations"]:
                print(f"ERROR: {len(report['violations'])} Core↔AI integration violations detected")
                for violation in report["violations"]:
                    print(f"  - {violation['from_module']} -> {violation['to_module']}: {violation['violation_type']}")
                return 2
            
            print(f"SUCCESS: Core↔AI integration validated")
            print(f"  - Validated bindings: {report['total_bindings']}")
            print(f"  - Violations: {len(report['violations'])}")
            print(f"  - Reports written to: {args.output}")
            
        else:
            # If no validate flag, run the full script
            report = validate_core_ai_integrity()
            write_integration_report(report, args.output)
            validate_output_schema(report)
            
            print(f"Core↔AI integration validation completed")
            print(f"  - Validated bindings: {report['total_bindings']}")
            print(f"  - Violations: {len(report['violations'])}")

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 3

if __name__ == "__main__":
    sys.exit(main())