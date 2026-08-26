#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-004}
# {Requirement IDs: FR-SCHEMA_COMPLIANCE}
# Test Type: UNIT_TEST

import json
import os
import pytest

def test_compliance_report_schema():
    """Verify compliance_report.json schema compliance."""
    report_path = "storage/data/compliance_report.json"
    
    # Report should exist
    assert os.path.exists(report_path), f"Compliance report not found at {report_path}"
    
    # Should be valid JSON
    with open(report_path, "r") as f:
        data = json.load(f)
    
    # Required fields from FR-SCHEMA_COMPLIANCE
    required_fields = ["compliance_score", "violations", "timestamp"]
    for field in required_fields:
        assert field in data, f"Compliance report missing required field: {field}"
    
    # compliance_score should be a number between 0 and 100
    assert isinstance(data["compliance_score"], (int, float)), "compliance_score should be a number"
    assert 0 <= data["compliance_score"] <= 100, "compliance_score should be between 0 and 100"
    
    # violations should be a list
    assert isinstance(data["violations"], list), "violations should be a list"
    
    # timestamp should be a string in ISO-8601 format
    assert isinstance(data["timestamp"], str), "timestamp should be a string"
    # Basic ISO-8601 format check
    assert "T" in data["timestamp"] or " " in data["timestamp"], "timestamp should be ISO-8601 format"

def test_purge_report_schema():
    """Verify purge_report.json schema compliance."""
    report_path = "storage/data/purge_report.json"
    
    # Report should exist if scripts have been executed
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
        
        # Required fields from FR-SCHEMA_COMPLIANCE
        required_fields = ["directories_removed", "files_removed", "referenced_files_blocked"]
        for field in required_fields:
            assert field in data, f"Purge report missing required field: {field}"
        
        # All fields should be lists
        for field in required_fields:
            assert isinstance(data[field], list), f"{field} should be a list"

def test_integration_binding_matrix_schema():
    """Verify integration_binding_matrix.json schema compliance."""
    report_path = "storage/data/import_validation_report.json"
    
    # Report should exist if scripts have been executed
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
        
        # Required fields from FR-SCHEMA_COMPLIANCE
        required_fields = ["bindings", "summary"]
        for field in required_fields:
            assert field in data, f"Integration binding matrix missing required field: {field}"
        
        # bindings should be a list
        assert isinstance(data["bindings"], list), "bindings should be a list"
        
        # Each binding should have required fields
        for binding in data["bindings"]:
            required_binding_fields = ["from", "to", "valid"]
            for field in required_binding_fields:
                assert field in binding, f"Binding missing required field: {field}"
        
        # summary should have required fields
        required_summary_fields = ["total", "valid", "invalid"]
        for field in required_summary_fields:
            assert field in data["summary"], f"Summary missing required field: {field}"
        
        # All summary fields should be numbers
        for field in required_summary_fields:
            assert isinstance(data["summary"][field], (int, float)), f"summary.{field} should be a number"

def test_reorg_audit_log_schema():
    """Verify reorg_audit_log.jsonl schema compliance."""
    log_path = "storage/data/reorg_audit_log.jsonl"
    
    # Log should exist
    assert os.path.exists(log_path), f"Audit log not found at {log_path}"
    
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
            
            # Required fields from FR-SCHEMA_COMPLIANCE
            required_fields = ["timestamp", "action", "source_path", "destination_path"]
            for field in required_fields:
                assert field in entry, f"Audit log entry {line_num} missing required field: {field}"
            
            # Validate field types
            assert isinstance(entry["timestamp"], str), f"Entry {line_num} timestamp should be a string"
            assert isinstance(entry["action"], str), f"Entry {line_num} action should be a string"
            assert isinstance(entry["source_path"], str), f"Entry {line_num} source_path should be a string"
            assert isinstance(entry["destination_path"], str), f"Entry {line_num} destination_path should be a string"
            
            # Validate action enum (from FR-SCHEMA_COMPLIANCE)
            assert entry["action"] in ["move", "delete", "create"], f"Entry {line_num} has invalid action: {entry['action']}"
