#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-005}
# {Requirement IDs: NFR-BACKWARD_COMPAT}
# Test Type: INTEGRITY_TEST

import subprocess
import os
import pytest

def test_backward_compatibility():
    """Test that existing test suite passes after reorganization."""
    
    # Run pytest on the M20 tests directory (the ones we're responsible for)
    # This simulates running tests on the implementation
    cmd = ["uv", "run", "pytest", "tests/M20/", "-q"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # The test suite should run successfully (exit code 0)
    # This verifies backward compatibility - that our changes don't break existing tests
    assert result.returncode == 0, f"Test suite should pass with exit code 0, got {result.returncode}.\nStdout: {result.stdout}\nStderr: {result.stderr}"
    
    # Verify that the core M20 test infrastructure is working
    # This ensures we haven't broken the test infrastructure itself
    assert "passed" in result.stdout or "passed" in result.stderr, \
        "Test suite should report successful test execution"

def test_implementation_cli_interfaces():
    """Test that CLI interfaces are working correctly."""
    
    # Test each of the three main CLI scripts
    scripts = [
        "scripts/checks/check_directory_structure.py",
        "scripts/checks/validate_3layer_pattern.py", 
        "scripts/checks/verify_legacy_cleanup.py"
    ]
    
    for script in scripts:
        # Test help flag - should exit with code 0
        result = subprocess.run(["uv", "run", "python", script, "--help"], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0, f"Script {script} help should exit 0, got {result.returncode}. Stderr: {result.stderr}"
        
        # Verify help contains usage information
        assert "usage:" in result.stdout.lower(), f"Script {script} help should contain usage information"
        
        # Test normal execution - should exit with code 0
        result = subprocess.run(["uv", "run", "python", script], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0, f"Script {script} normal execution should exit 0, got {result.returncode}. Stderr: {result.stderr}"

def test_exported_interfaces():
    """Test that exported interfaces are properly accessible."""
    
    # Test that the checks module can be imported
    import_commands = [
        "from scripts.checks.check_directory_structure import scan_repository",
        "from scripts.checks.validate_3layer_pattern import analyze_imports",
        "from scripts.checks.verify_legacy_cleanup import find_legacy_directories"
    ]
    
    for import_cmd in import_commands:
        # Try to import the module
        python_cmd = ["python3", "-c", f"import sys; sys.path.insert(0, '.'); {import_cmd}"]
        import_result = subprocess.run(python_cmd, capture_output=True, text=True)
        
        assert import_result.returncode == 0, f"Failed to import {import_cmd}: {import_result.stderr}"
