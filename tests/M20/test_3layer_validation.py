#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-003}
# {Requirement IDs: FR-COMPLIANCE_CHECK}
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

def test_validate_3layer_pattern_execution():
    """Verify validate_3layer_pattern.py executes and writes integration binding matrix."""
    script_path = "scripts/checks/validate_3layer_pattern.py"
    
    result = run_script(script_path)
    
    # Should exit with code 0 for successful execution
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. Stderr: {result.stderr}"
    
    # Should create a binding matrix report (actual filename from script)
    report_path = "storage/data/import_validation_report.json"
    assert os.path.exists(report_path), f"Report file {report_path} was not created"
    
    # Report should be valid JSON with required fields
    with open(report_path, "r") as f:
        data = json.load(f)
    
    # Required fields from schema
    assert "summary" in data, "summary field missing from report"
    
    # summary should have total, valid, invalid fields
    summary = data["summary"]
    assert "total_files_analyzed" in summary, "summary missing total_files_analyzed"
    assert "valid_imports" in summary, "summary missing valid_imports"
    assert "invalid_imports" in summary, "summary missing invalid_imports"
    
    # According to verification protocol, invalid should equal 0
    assert summary["invalid_imports"] == 0, f"Expected 0 invalid imports, got {summary['invalid_imports']}"

def test_validate_3layer_pattern_help():
    """Verify that help functionality is properly documented."""
    script_path = "scripts/checks/validate_3layer_pattern.py"
    
    result = run_script(script_path, ["--help"])
    
    # Should exit with code 0 for help
    assert result.returncode == 0, f"Help should exit 0, got {result.returncode}"
    
    # Should contain documentation
    assert "usage:" in result.stdout.lower(), "Help should contain usage information"
    assert "--strict" in result.stdout, "Help should document --strict option"

def test_validate_3layer_pattern_custom_output():
    """Verify custom output path functionality."""
    script_path = "scripts/checks/validate_3layer_pattern.py"
    
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_report = os.path.join(temp_dir, "custom_validation.json")
        
        result = run_script(script_path, ["--output", custom_report])
        
        # Should exit with code 0
        assert result.returncode == 0, f"Custom output should exit 0, got {result.returncode}"
        
        # Should create custom report
        assert os.path.exists(custom_report), f"Custom report {custom_report} was not created"
        
        # Should validate schema
        with open(custom_report, "r") as f:
            data = json.load(f)
        
        # Should have summary
        assert "summary" in data, "Custom report missing summary"
        
        # Summary should have total, valid, invalid fields
        assert "invalid_imports" in data["summary"], "Custom report summary missing invalid_imports"
        assert data["summary"]["invalid_imports"] == 0, "Custom report should have 0 invalid imports"
