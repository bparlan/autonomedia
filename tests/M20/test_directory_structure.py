#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-001}
# {Requirement IDs: FR-DIR_AUDIT_SCRIPT}
# Test Type: IMPLEMENTATION_CHECK

import json
import os
import subprocess
import pytest
from pathlib import Path

def run_script(script_path, args=None, cwd=None):
    """Helper to run a script with given arguments."""
    cmd = ["uv", "run", "python", script_path]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

def test_check_directory_structure_execution():
    """Verify that check_directory_structure.py executes directly and produces a compliance report."""
    script_path = "scripts/checks/check_directory_structure.py"
    
    # Execute target script per CLI contract
    result = run_script(script_path)
    
    # Should exit with code 0 for successful execution
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. Stderr: {result.stderr}"
    
    # Should create a compliance report
    report_path = "storage/data/compliance_report.json"
    assert os.path.exists(report_path), f"Report file {report_path} was not created"
    
    # Report should be valid JSON with required fields
    with open(report_path, "r") as f:
        data = json.load(f)
    
    # Required fields from schema
    assert "compliance_score" in data, "compliance_score missing from report"
    assert "violations" in data, "violations field missing from report"
    assert "timestamp" in data, "timestamp field missing from report"
    
    # compliance_score should be a number between 0 and 100
    assert isinstance(data["compliance_score"], (int, float)), "compliance_score should be a number"
    assert 0 <= data["compliance_score"] <= 100, "compliance_score should be between 0 and 100"

def test_check_directory_structure_help():
    """Verify that help functionality is properly documented."""
    script_path = "scripts/checks/check_directory_structure.py"
    
    result = run_script(script_path, ["--help"])
    
    # Should exit with code 0 for help
    assert result.returncode == 0, f"Help should exit 0, got {result.returncode}"
    
    # Should contain documentation
    assert "usage:" in result.stdout.lower(), "Help should contain usage information"
    assert "--output" in result.stdout, "Help should document --output option"

def test_check_directory_structure_custom_output():
    """Verify custom output path functionality."""
    script_path = "scripts/checks/check_directory_structure.py"
    
    # Create temporary directory for custom output
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_report = os.path.join(temp_dir, "custom_report.json")
        
        result = run_script(script_path, ["--output", custom_report])
        
        # Should exit with code 0
        assert result.returncode == 0, f"Custom output should exit 0, got {result.returncode}"
        
        # Should create custom report
        assert os.path.exists(custom_report), f"Custom report {custom_report} was not created"
        
        # Should validate schema
        with open(custom_report, "r") as f:
            data = json.load(f)
        
        # Should have compliance_score
        assert "compliance_score" in data, "Custom report missing compliance_score"
