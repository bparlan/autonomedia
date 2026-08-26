#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-002}
# {Requirement IDs: FR-LEGACY_PURGE}
# Test Type: IMPLEMENTATION_CHECK

import json
import os
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path

def run_script(script_path, args=None, cwd=None):
    """Helper to run a script with given arguments."""
    cmd = ["uv", "run", "python", script_path]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

def test_verify_legacy_cleanup_dry_run():
    """Test verify_legacy_cleanup.py dry-run behavior."""
    script_path = "scripts/checks/verify_legacy_cleanup.py"
    
    # Run dry-run mode
    result = run_script(script_path, ["--dry-run"])
    
    # Should exit with code 0 for dry-run
    assert result.returncode == 0, f"Dry-run should exit 0, got {result.returncode}. Stderr: {result.stderr}"
    
    # Should produce a report
    report_path = "storage/data/purge_report.json"
    assert os.path.exists(report_path), f"Purge report not created at {report_path}"
    
    # Report should be valid JSON
    with open(report_path, "r") as f:
        data = json.load(f)
    
    # Check report structure
    required_keys = ["directories_removed", "files_removed", "referenced_files_blocked"]
    for key in required_keys:
        assert key in data, f"Report missing required key: {key}"

def test_verify_legacy_cleanup_execute():
    """Test verify_legacy_cleanup.py execute behavior with actual legacy directory."""
    script_path = "scripts/checks/verify_legacy_cleanup.py"
    
    # Run execute mode to see what it does in the current environment
    result = run_script(script_path, ["--execute"])
    
    # Execute should complete without errors
    assert result.returncode == 0, f"Execute mode should exit 0, got {result.returncode}. Stderr: {result.stderr}"
    
    # Check that report was created/updated
    report_path = "storage/data/purge_report.json"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
        
        # Report should have data
        assert "directories_removed" in data, "Report missing directories_removed"
        assert "files_removed" in data, "Report missing files_removed"
        assert "referenced_files_blocked" in data, "Report missing referenced_files_blocked"
        
        # All values should be lists
        assert isinstance(data["directories_removed"], list), "directories_removed should be a list"
        assert isinstance(data["files_removed"], list), "files_removed should be a list"
        assert isinstance(data["referenced_files_blocked"], list), "referenced_files_blocked should be a list"
