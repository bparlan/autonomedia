#!/usr/bin/env python3
"""
Integration Binding Validation Tests for M20S2

This test file implements the verification protocol VER-M20S2 defined in
milestones/M20/VER-M20S2V.md. It validates all 5 verification items:

- VI-001: FR-INTEGRITY_CORE_AI_BINDING (SCRIPT_EXECUTION)
- VI-002: FR-INTEGRITY_PLATFORM_CORE_BINDING (SCRIPT_EXECUTION)
- VI-003: FR-INTEGRITY_WEB_DATA_BINDING (SCRIPT_EXECUTION)
- VI-004: FR-INTEGRITY_PLATFORM_ISOLATION (SCHEMA_CONTRACT)
- VI-005: FR-INTEGRITY_RUNTIME_DETERMINISM (SCRIPT_EXECUTION)

{Verification IDs: VI-001, VI-002, VI-003, VI-004, VI-005}
{Requirement IDs: FR-INTEGRITY_CORE_AI_BINDING, FR-INTEGRITY_PLATFORM_CORE_BINDING, FR-INTEGRITY_WEB_DATA_BINDING, FR-INTEGRITY_PLATFORM_ISOLATION, FR-INTEGRITY_RUNTIME_DETERMINISM}
# Test Type: INTEGRATION_TEST
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Custom exceptions for integration binding validation
class CoreAIImportViolation(Exception):
    """Raised when core infrastructure imports from AI engine."""
    pass

class PlatformCoreIsolationViolation(Exception):
    """Raised when platform adapters import from core infrastructure."""
    pass

class WebDataRegistryViolation(Exception):
    """Raised when web application imports from data registry."""
    pass

class CrossPlatformImportViolation(Exception):
    """Raised when cross-platform imports detected."""
    pass

class DeterminismViolation(Exception):
    """Raised when determinism checks fail."""
    pass
def run_script(script_path, output_file=None, compare_files=None):
    """Run a validation script and return the result."""
    cmd = [sys.executable, script_path]

    if output_file:
        cmd.extend(["--validate", "--output", output_file])

    if compare_files:
        cmd.extend(["--compare"] + compare_files)

    env = os.environ.copy()
    env["REPO_ROOT"] = "."

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return result
def get_file_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
def remove_timestamps(data):
    """Remove timestamp fields from JSON data for determinism comparison."""
    if isinstance(data, dict):
        # Remove timestamp fields
        for key in list(data.keys()):
            if key.endswith("_time") or key == "validation_round" or key == "timestamp" or key == "checksum":
                data.pop(key)
            elif isinstance(data[key], (dict, list)):
                remove_timestamps(data[key])
    elif isinstance(data, list):
        for item in data:
            remove_timestamps(item)
    return data
def test_vi_001_core_ai_binding_validation():
    """Test VI-001: FR-INTEGRITY_CORE_AI_BINDING - Core infrastructure ↔ AI engine integration validation."""
    output_file = "storage/data/integration_core_ai_binding.json"

    # Clean up previous run
    if os.path.exists(output_file):
        os.remove(output_file)

    # Run validation script (VI-001 verification method: SCRIPT_EXECUTION)
    result = run_script("scripts/checks/integrity_core_ai.py", output_file=output_file)

    # Verify exit code (Expected: 0, 2, or 3 according to VI-001)
    assert result.returncode in [0, 2, 3], f"Core-AI validation failed with exit code {result.returncode}: {result.stderr}"
    print(f"✓ Core-AI validation script executed successfully (exit code: {result.returncode})")

    # Verify output file was created (Expected evidence: output file with validated_bindings array)
    assert os.path.exists(output_file), f"Output file {output_file} was not created"
    print(f"✓ Output file {output_file} was created")

    # Load and validate JSON schema
    with open(output_file, "r") as f:
        data = json.load(f)

    # Core-AI integration binding schema validation
    assert "validated_bindings" in data, "validated_bindings field missing"
    assert "violations" in data, "violations field missing"
    assert "total_bindings" in data, "total_bindings field missing"
    assert isinstance(data["validated_bindings"], list), "validated_bindings must be a list"
    assert isinstance(data["violations"], list), "violations must be a list"
    assert isinstance(data["total_bindings"], int), "total_bindings must be an integer"
    assert data["total_bindings"] >= 0, "total_bindings must be non-negative"

    print(f"✓ Integration report contains valid schema with {data['total_bindings']} total bindings")
    print(f"  - {len(data['validated_bindings'])} validated bindings")
    print(f"  - {len(data['violations'])} violations found")
    print()

    # Verify the JSON schema matches the specification
    expected_schema = {
        "validated_bindings": list,
        "violations": list,
        "total_bindings": int
    }

    for field, field_type in expected_schema.items():
        assert field in data, f"Schema field {field} missing"
        assert isinstance(data[field], field_type), f"Field {field} must be {field_type}"

    print(f"✓ Integration report schema compliance verified")
    print(f"VI-001 SATISFIED")
    print()
def test_vi_002_platform_core_binding_validation():
    """Test VI-002: FR-INTEGRITY_PLATFORM_CORE_BINDING - Platform adapters ↔ core infrastructure integration validation."""
    output_file = "storage/data/integration_platform_core_binding.json"

    # Clean up previous run
    if os.path.exists(output_file):
        os.remove(output_file)

    # Run validation script (VI-002 verification method: SCRIPT_EXECUTION)
    result = run_script("scripts/checks/integrity_platform_core.py", output_file=output_file)

    # Verify exit code (Expected: 0 or 2 according to VI-002)
    assert result.returncode in [0, 2], f"Platform-core validation failed with exit code {result.returncode}: {result.stderr}"
    print(f"✓ Platform-core validation script executed successfully (exit code: {result.returncode})")

    # Verify output file was created (Expected evidence: output file with isolation reports)
    assert os.path.exists(output_file), f"Output file {output_file} was not created"
    print(f"✓ Output file {output_file} was created")

    # Load and validate JSON schema
    with open(output_file, "r") as f:
        data = json.load(f)

    # Platform-core integration binding schema validation
    assert "validated_bindings" in data, "validated_bindings field missing"
    assert "violations" in data, "violations field missing"
    assert "isolation_score" in data, "isolation_score field missing"
    assert isinstance(data["validated_bindings"], list), "validated_bindings must be a list"
    assert isinstance(data["violations"], list), "violations must be a list"
    assert isinstance(data["isolation_score"], (int, float)), "isolation_score must be a number"
    assert 0 <= data["isolation_score"] <= 100, "isolation_score must be between 0 and 100"

    print(f"✓ Integration report contains valid schema with isolation_score: {data['isolation_score']}")
    print(f"  - {len(data['validated_bindings'])} validated bindings")
    print(f"  - {len(data['violations'])} violations found")
    print()

    # Verify the JSON schema matches the specification
    expected_schema = {
        "validated_bindings": list,
        "violations": list,
        "isolation_score": (int, float)
    }

    for field, field_types in expected_schema.items():
        assert field in data, f"Schema field {field} missing"
        assert isinstance(data[field], field_types), f"Field {field} must be {field_types}"

    print(f"✓ Integration report schema compliance verified")
    print(f"VI-002 SATISFIED")
    print()
def test_vi_003_web_data_binding_validation():
    """Test VI-003: FR-INTEGRITY_WEB_DATA_BINDING - Web application ↔ data registry integration validation."""
    output_file = "storage/data/integration_web_data_binding.json"

    # Clean up previous run
    if os.path.exists(output_file):
        os.remove(output_file)

    # Run validation script (VI-003 verification method: SCRIPT_EXECUTION)
    result = run_script("scripts/checks/integrity_web_data.py", output_file=output_file)

    # Verify exit code (Expected: 0 or 2 according to VI-003)
    assert result.returncode in [0, 2], f"Web-data validation failed with exit code {result.returncode}: {result.stderr}"
    print(f"✓ Web-data validation script executed successfully (exit code: {result.returncode})")

    # Verify output file was created (Expected evidence: output file with web-data integration reports)
    assert os.path.exists(output_file), f"Output file {output_file} was not created"
    print(f"✓ Output file {output_file} was created")

    # Load and validate JSON schema
    with open(output_file, "r") as f:
        data = json.load(f)

    # Web-data integration binding schema validation
    assert "validated_bindings" in data, "validated_bindings field missing"
    assert "violations" in data, "violations field missing"
    assert "valid_access" in data, "valid_access field missing"
    assert isinstance(data["validated_bindings"], list), "validated_bindings must be a list"
    assert isinstance(data["violations"], list), "violations must be a list"
    assert isinstance(data["valid_access"], bool), "valid_access must be a boolean"

    print(f"✓ Integration report contains valid schema with valid_access: {data['valid_access']}")
    print(f"  - {len(data['validated_bindings'])} validated bindings")
    print(f"  - {len(data['violations'])} violations found")
    print()

    # Verify the JSON schema matches the specification
    expected_schema = {
        "validated_bindings": list,
        "violations": list,
        "valid_access": bool
    }

    for field, field_type in expected_schema.items():
        assert field in data, f"Schema field {field} missing"
        assert isinstance(data[field], field_type), f"Field {field} must be {field_type}"

    print(f"✓ Integration report schema compliance verified")
    print(f"VI-003 SATISFIED")
    print()
def test_vi_004_platform_isolation_validation():
    """Test VI-004: FR-INTEGRITY_PLATFORM_ISOLATION - Platform isolation schema validation."""
    output_file = "storage/data/platform_isolation_report.json"

    # Run validation script (VI-004 verification method: SCHEMA_CONTRACT)
    result = run_script("scripts/checks/integrity_platform_isolation.py", output_file=output_file)

    # Verify exit code (Expected: 0 according to VI-004)
    assert result.returncode == 0, f"Platform isolation validation failed with exit code {result.returncode}: {result.stderr}"
    print(f"✓ Platform isolation validation script executed successfully (exit code: {result.returncode})")

    # Verify output file was created
    assert os.path.exists(output_file), f"Output file {output_file} was not created"
    print(f"✓ Output file {output_file} was created")

    # Load and validate JSON schema (VI-004 Expected evidence: Valid platform_isolation_report.json schema)
    with open(output_file, "r") as f:
        data = json.load(f)

    # Platform isolation schema validation
    assert "fully_isolated_platforms" in data, "fully_isolated_platforms field missing"
    assert "cross_platform_violations" in data, "cross_platform_violations field missing"
    assert "isolation_score" in data, "isolation_score field missing"
    assert isinstance(data["fully_isolated_platforms"], list), "fully_isolated_platforms must be a list"
    assert isinstance(data["cross_platform_violations"], list), "cross_platform_violations must be a list"
    assert isinstance(data["isolation_score"], (int, float)), "isolation_score must be a number"
    assert 0 <= data["isolation_score"] <= 100, "isolation_score must be between 0 and 100"

    print(f"✓ Isolation report contains valid schema with isolation_score: {data['isolation_score']}")
    print(f"  - {len(data['fully_isolated_platforms'])} fully isolated platforms")
    print(f"  - {len(data['cross_platform_violations'])} cross-platform violations")
    print()

    # Verify the JSON schema matches the specification
    expected_schema = {
        "fully_isolated_platforms": list,
        "cross_platform_violations": list,
        "isolation_score": (int, float)
    }

    for field, field_types in expected_schema.items():
        assert field in data, f"Schema field {field} missing"
        assert isinstance(data[field], field_types), f"Field {field} must be {field_types}"

    print(f"✓ Platform isolation report schema compliance verified")
    print(f"VI-004 SATISFIED")
    print()
def test_vi_005_runtime_determinism_validation():
    """Test VI-005: FR-INTEGRITY_RUNTIME_DETERMINISM - Runtime determinism validation."""
    output_file1 = "storage/data/integration_binding_matrix_1.json"
    output_file2 = "storage/data/integration_binding_matrix_2.json"

    # Clean up previous runs
    for output_file in [output_file1, output_file2]:
        if os.path.exists(output_file):
            os.remove(output_file)

    # Generate first binding matrix (VI-005 verification method: SCRIPT_EXECUTION)
    # Based on VER-M20S2V.md line 68: uv run python scripts/checks/integrity_runtime_determinism.py --validate --compare storage/data/integration_binding_matrix_1.json storage/data/integration_binding_matrix_2.json
    # When called with --validate and --output, it generates a binding matrix
    result1 = run_script("scripts/checks/integrity_runtime_determinism.py", output_file=output_file1)
    assert result1.returncode == 0, f"First determinism matrix generation failed: {result1.stderr}"

    # Generate second binding matrix
    result2 = run_script("scripts/checks/integrity_runtime_determinism.py", output_file=output_file2)
    assert result2.returncode == 0, f"Second determinism matrix generation failed: {result2.stderr}"

    print(f"✓ Runtime determinism validation scripts executed successfully")
    print(f"  - Matrix 1: {output_file1}")
    print(f"  - Matrix 2: {output_file2}")

    # Load both matrices
    with open(output_file1, "r") as f1, open(output_file2, "r") as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Remove validation_round and generated_at for deterministic comparison
    # (These fields contain timestamps which differ between runs)
    data1_clean = remove_timestamps(data1)
    data2_clean = remove_timestamps(data2)

    # Verify matrices are identical after removing timestamps (VI-005 Expected evidence: checksum_match=true)
    assert data1_clean == data2_clean, "Output of integrity_runtime_determinism.py is not deterministic"

    print(f"✓ Binding matrices are deterministic (checksum_match=true)")
    print(f"VI-005 SATISFIED")
    print()
    print("All 5 verification items (VI-001 to VI-005) have been validated successfully!")
    print("=" * 80)
if __name__ == "__main__":
    test_vi_001_core_ai_binding_validation()
    test_vi_002_platform_core_binding_validation()
    test_vi_003_web_data_binding_validation()
    test_vi_004_platform_isolation_validation()
    test_vi_005_runtime_determinism_validation()