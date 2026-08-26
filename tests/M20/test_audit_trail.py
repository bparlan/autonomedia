#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-008}
# {Requirement IDs: NFR-AUDIT_TRAIL}
# Test Type: UNIT_TEST

import json
import os
import pytest

def test_reorg_audit_log_format():
    """Verify storage/data/reorg_audit_log.jsonl is a valid JSONL audit trail."""
    
    log_path = "storage/data/reorg_audit_log.jsonl"
    
    # Log file should exist
    assert os.path.exists(log_path), f"Audit log not found at {log_path}"
    
    # Log file should not be empty
    assert os.path.getsize(log_path) > 0, "Audit log file is empty"
    
    # Read and validate each line
    with open(log_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse JSON
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                pytest.fail(f"Line {line_num} is not valid JSON: {line}. Error: {e}")
            
            # Required fields from verification protocol
            required_fields = ["timestamp", "action", "source_path", "destination_path"]
            for field in required_fields:
                assert field in entry, f"Audit log entry {line_num} missing required field: {field}"
            
            # Validate field types
            assert isinstance(entry["timestamp"], str), f"Entry {line_num} timestamp should be a string"
            assert isinstance(entry["action"], str), f"Entry {line_num} action should be a string"
            assert isinstance(entry["source_path"], str), f"Entry {line_num} source_path should be a string"
            assert isinstance(entry["destination_path"], str), f"Entry {line_num} destination_path should be a string"
            
            # Validate action enum
            assert entry["action"] in ["move", "delete", "create"], f"Entry {line_num} has invalid action: {entry['action']}"
            
            # Validate timestamp format (basic check)
            assert "T" in entry["timestamp"] or " " in entry["timestamp"], f"Entry {line_num} timestamp should be ISO-8601 format: {entry['timestamp']}"

def test_audit_log_content():
    """Test that audit log contains expected entries from reorganization scripts."""
    
    log_path = "storage/data/reorg_audit_log.jsonl"
    
    # Read all entries
    entries = []
    with open(log_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entry = json.loads(line)
                entries.append(entry)
    
    # Should have at least one entry (from script execution)
    assert len(entries) > 0, "Audit log should contain at least one entry"
    
    # Check that we have various audit actions
    audit_actions = [entry["action"] for entry in entries]
    
    # Should have create actions (from reorg_audit_log.py initialization)
    assert "create" in audit_actions, "Audit log should contain create actions"
    
    # Validate that all entries have proper structure
    for entry in entries:
        # Check that action is one of the expected values
        assert entry["action"] in ["move", "delete", "create"], \
            f"Invalid audit action: {entry['action']}"
        
        # Check that source and destination paths are consistent
        # For create actions, source_path might be empty
        if entry["action"] == "create":
            assert entry["source_path"] == "" or entry["source_path"] is None, \
                "Create action should have empty source_path"
        
        # All entries should have timestamp in reasonable format
        assert len(entry["timestamp"]) >= 10, "Timestamp should be at least 10 characters"
        assert entry["timestamp"][4] == "-", "Timestamp should have YYYY-MM format"
