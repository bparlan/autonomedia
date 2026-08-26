#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-007}
# {Requirement IDs: NFR-DETERMINISM}
# Test Type: IMPLEMENTATION_CHECK

import json
import os
import subprocess
import hashlib
import pytest
from pathlib import Path

def get_file_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    if not os.path.exists(file_path):
        return None
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def test_deterministic_output():
    """Test that scripts produce deterministic output."""
    
    # Test check_directory_structure.py
    script1 = "scripts/checks/check_directory_structure.py"
    report1 = "storage/data/compliance_report.json"
    
    # Run script twice
    result1 = subprocess.run(["uv", "run", "python", script1], capture_output=True, text=True)
    result2 = subprocess.run(["uv", "run", "python", script1], capture_output=True, text=True)
    
    # Both runs should succeed
    assert result1.returncode == 0, f"First run failed: {result1.stderr}"
    assert result2.returncode == 0, f"Second run failed: {result2.stderr}"
    
    # Check that report files exist
    assert os.path.exists(report1), f"Report file {report1} not created"
    
    # Calculate checksums of both reports
    checksum1 = get_file_checksum(report1)
    checksum2 = get_file_checksum(report1)
    
    # Checksums should be identical
    assert checksum1 == checksum2, f"Checksum mismatch: {checksum1} != {checksum2}"
    
    # Test validate_3layer_pattern.py
    script2 = "scripts/checks/validate_3layer_pattern.py"
    report2 = "storage/data/import_validation_report.json"
    
    # Run script twice
    result1 = subprocess.run(["uv", "run", "python", script2], capture_output=True, text=True)
    result2 = subprocess.run(["uv", "run", "python", script2], capture_output=True, text=True)
    
    # Both runs should succeed
    assert result1.returncode == 0, f"First run failed: {result1.stderr}"
    assert result2.returncode == 0, f"Second run failed: {result2.stderr}"
    
    # Check that report files exist
    assert os.path.exists(report2), f"Report file {report2} not created"
    
    # Calculate checksums of both reports
    checksum1 = get_file_checksum(report2)
    checksum2 = get_file_checksum(report2)
    
    # Checksums should be identical
    assert checksum1 == checksum2, f"Checksum mismatch: {checksum1} != {checksum2}"
