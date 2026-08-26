#!/usr/bin/env python3
"""
Platform-Core Integration Binding Validation Script

Implements FR-INTEGRITY_PLATFORM_CORE_BINDING: Validates Core Infrastructure ↔ Platform Adapters integration boundaries.

Produces: storage/data/integration_platform_core_binding.json

Exit codes:
0: Success - all platform-core integrations valid
2: Platform-core violations detected
3: Analysis failed
"""

import sys
import json
import argparse
import ast
from datetime import datetime
from pathlib import Path

# Custom exception for import violations
class PlatformCoreIsolationViolation(Exception):
    """Raised when platform adapters import from core infrastructure."""
    def __init__(self, message: str, import_path: str):
        super().__init__(message)
        self.import_path = import_path

# Script implementation flag
FR_INTEGRITY_PLATFORM_CORE_BINDING = True

# Platform adapters paths
PLATFORM_PATHS = [
    "src/autonomedia/platforms/",
]

# Core infrastructure paths
CORE_INFRASTRUCTURE_PATHS = [
    "src/autonomedia/core/",
    "src/autonomedia/database/",
    "src/autonomedia/content/",
]

def validate_platform_core_integrity(repo_root: str = ".") -> dict:
    """Validate Platform ↔ Core Infrastructure integration boundaries.

    Args:
        repo_root: Repository root path

    Returns:
        Dict with validated_bindings, violations, total_bindings, and generated_at
    """
    repo_path = Path(repo_root).resolve()
    validated_bindings = []
    violations = []
    total_bindings = 0

    # Scan for imports in platform adapters that reference core (these are violations)
    for py_file in repo_path.rglob("*.py"):
        # Only check platform adapter files
        if not any(platform_path in str(py_file) for platform_path in PLATFORM_PATHS):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_core_import(alias.name):
                            violations.append({
                                "from_module": str(py_file.relative_to(repo_path)),
                                "to_module": alias.name,
                                "violation_type": "isolation_violation",
                                "severity": "MEDIUM"
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module and _is_core_import(node.module):
                        violations.append({
                            "from_module": str(py_file.relative_to(repo_path)),
                            "to_module": node.module,
                            "violation_type": "isolation_violation",
                            "severity": "MEDIUM"
                        })

        except (SyntaxError, UnicodeDecodeError, PermissionError):
            continue

    # Scan for imports in core infrastructure that reference platform adapters (these are valid bindings)
    for py_file in repo_path.rglob("*.py"):
        # Skip platform files themselves
        if any(platform_path in str(py_file) for platform_path in PLATFORM_PATHS):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_platform_import(alias.name):
                            validated_bindings.append({
                                "from_module": str(py_file.relative_to(repo_path)),
                                "to_module": alias.name,
                                "binding_type": "interface",
                                "valid": True
                            })
                            total_bindings += 1

                if isinstance(node, ast.ImportFrom):
                    if node.module and _is_platform_import(node.module):
                        validated_bindings.append({
                            "from_module": str(py_file.relative_to(repo_path)),
                            "to_module": node.module,
                            "binding_type": "interface",
                            "valid": True
                        })
                        total_bindings += 1

        except (SyntaxError, UnicodeDecodeError, PermissionError):
            continue

    return {
        "validated_bindings": validated_bindings,
        "violations": violations,
        "total_bindings": total_bindings,
        "generated_at": datetime.now().isoformat()
    }

def check_isolation_violations(repo_root: str = ".") -> list:
    """Detect platform-core isolation violations.

    Args:
        repo_root: Repository root path

    Returns:
        List of isolation violation dictionaries
    """
    repo_path = Path(repo_root).resolve()
    isolation_violations = []

    # Scan for violations in platform adapters
    for py_file in repo_path.rglob("*.py"):
        if not any(platform_path in str(py_file) for platform_path in PLATFORM_PATHS):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_core_import(alias.name):
                            isolation_violations.append({
                                "platform_file": str(py_file.relative_to(repo_path)),
                                "core_module": alias.name,
                                "import_type": "direct_import",
                                "severity": "MEDIUM"
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module and _is_core_import(node.module):
                        isolation_violations.append({
                            "platform_file": str(py_file.relative_to(repo_path)),
                            "core_module": node.module,
                            "import_type": "from_import",
                            "severity": "MEDIUM"
                        })

        except (SyntaxError, UnicodeDecodeError, PermissionError):
            continue

    return isolation_violations

def generate_isolation_report(report: dict, output_path: str) -> None:
    """Generate isolation report and write to file.

    Args:
        report: Isolation validation report
        output_path: Output file path
    """
    try:
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

    except (OSError, IOError) as e:
        print(f"Error writing isolation report to {output_path}: {e}")
        raise

def _is_core_import(import_path: str) -> bool:
    """Check if import path is from core infrastructure."""
    normalized = import_path.replace(".", "/")
    return any(
        normalized.startswith(pattern.rstrip("/")) or
        import_path.startswith(pattern.replace("/", "."))
        for pattern in CORE_INFRASTRUCTURE_PATHS
    )

def _is_platform_import(import_path: str) -> bool:
    """Check if import path is from platform adapters."""
    normalized = import_path.replace(".", "/")
    return any(
        normalized.startswith(pattern.rstrip("/")) or
        import_path.startswith(pattern.replace("/", "."))
        for pattern in PLATFORM_PATHS
    )

def validate_output_schema(report: dict) -> None:
    """Validate output schema for platform-core isolation report."""
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
    """Main entry point for platform-core isolation validation script."""
    parser = argparse.ArgumentParser(description="Platform-Core Isolation Validation")
    parser.add_argument("--validate", "-v", action="store_true", help="Validate platform-core isolation")
    parser.add_argument("--output", "-o", default="storage/data/integration_platform_core_binding.json", help="Output report path")

    args = parser.parse_args()

    try:
        if args.validate:
            # Validate platform-core integration
            report = validate_platform_core_integrity()

            # Check for isolation violations
            isolation_violations = check_isolation_violations()

            # Write reports
            generate_isolation_report(report, args.output)

            # Validate output schema
            validate_output_schema(report)

            # Check for violations
            if report["violations"]:
                print(f"ERROR: {len(report['violations'])} platform-core isolation violations detected")
                for violation in report["violations"]:
                    print(f"  - {violation['from_module']} -> {violation['to_module']}: {violation['violation_type']}")
                return 2

            print(f"SUCCESS: Platform-core isolation validated")
            print(f"  - Validated bindings: {report['total_bindings']}")
            print(f"  - Isolation violations: {len(report['violations'])}")
            print(f"  - Reports written to: {args.output}")

        else:
            # If no validate flag, run the full script
            report = validate_platform_core_integrity()
            generate_isolation_report(report, args.output)
            validate_output_schema(report)

            print(f"Platform-core isolation validation completed")
            print(f"  - Validated bindings: {report['total_bindings']}")
            print(f"  - Isolation violations: {len(report['violations'])}")

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 3

if __name__ == "__main__":
    sys.exit(main())