# Verification Protocol: VER-M20S3V - FR-SUCCESS_CRITERIA_PROTOCOL

## Overview
This verification protocol validates FR-SUCCESS_CRITERIA_PROTOCOL, the deterministic success criteria verification protocol implementation for M20 across all layers.

## Specification Reference
- **FR ID**: FR-SUCCESS_CRITERIA_PROTOCOL
- **Type**: CLI Executable Contract
- **Interface Contract**: `uv run python scripts/checks/success_criteria_protocol.py --verify --output storage/data/success_criteria_report.json`
- **Expected Behavior**: Validates all M20 success criteria through deterministic verification protocol. Executes verification scripts for M20S1 compliance, M20S2 integration bindings, and M20S3 protocol itself. Produces unified compliance report with overall success determination.

## Verification Test Matrix

### Test Category 1: CLI Interface and Execution

**VI-SCP-001**: Test CLI Interface Contract
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: Interface Contract
- **Test Type**: CLI_TEST
- **Requirement**: Script must accept `--verify --output storage/data/success_criteria_report.json`
- **Verifiable Actions**:
  1. Execute: `uv run python scripts/checks/success_criteria_protocol.py --verify --output storage/data/success_criteria_report.json`
  2. Verify exit code is 0 when verification completes successfully
  3. Confirm output file: `storage/data/success_criteria_report.json` exists
  4. Validate JSON structure and content

**VI-SCP-002**: Test Script Execution and Exit Codes
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: Observable Boundary
- **Test Type**: UNIT_TEST
- **Requirement**: Exit codes 0, 2, 3 for different scenarios
- **Verifiable Actions**:
  1. Execute successful verification → verify exit code 0
  2. Simulate criteria failures → verify exit code 2
  3. Cause verification failure (e.g., script error) → verify exit code 3

### Test Category 2: Output Schema and Content

**VI-SCP-003**: Test Output Schema Contract
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: Observable Boundary
- **Test Type**: SCHEMA_CONTRACT
- **Requirement**: Output must contain specific fields with correct types
- **Required Fields**:
  - `verified_criteria`: list or dict of successfully verified criteria
  - `failed_criteria`: list or dict of failed criteria
  - `overall_success`: boolean indicating complete success
  - `compliance_score`: float between 0.0 and 1.0
- **Verifiable Actions**:
  1. Validate JSON structure matches schema
  2. Verify all required fields exist
  3. Validate field types and constraints
  4. Ensure consistency between fields (e.g., `overall_success=True` requires `failed_criteria=[]`)

### Test Category 3: Module Exports and Public Interface

**VI-SCP-004**: Test verify_m20_criteria() Function
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: New Module
- **Test Type**: UNIT_TEST
- **Requirement**: Function exports and behavior
- **Verifiable Actions**:
  1. Import `verify_m20_criteria` from `scripts.checks.success_criteria_protocol`
  2. Execute function and verify return type is dict
  3. Validate returned dict contains M20 criteria verification results
  4. Ensure function includes deterministic audit trail logging

**VI-SCP-005**: Test generate_success_report() Function
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: New Module
- **Test Type**: UNIT_TEST
- **Requirement**: Report generation functionality
- **Verifiable Actions**:
  1. Import `generate_success_report` from `scripts.checks.success_criteria_protocol`
  2. Execute with test data → verify dict output
  3. Validate report structure contains all required fields
  4. Ensure function includes deterministic audit trail logging

**VI-SCP-006**: Test SuccessCriteriaViolation Exception
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: Public Interface
- **Test Type**: UNIT_TEST
- **Requirement**: Exception class exports and behavior
- **Verifiable Actions**:
  1. Import `SuccessCriteriaViolation` from `scripts.checks.success_criteria_protocol`
  2. Raise and catch exception to verify type and message
  3. Test exception includes error context about failed criteria

**VI-SCP-007**: Test SUCCESS_CRITERIA_MAP Constant
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: Public Interface
- **Test Type**: UNIT_TEST
- **Requirement**: Constants exports and structure
- **Verifiable Actions**:
  1. Import `SUCCESS_CRITERIA_MAP` from `scripts.checks.success_criteria_protocol`
  2. Verify map type is dict[str, list[str]]
  3. Validate map structure contains M20 criteria definitions
  4. Ensure map includes all expected M20 success criteria keys

### Test Category 4: Deterministic Execution and Integration

**VI-SCP-008**: Test Deterministic Verification Protocol
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: Expected Behavior
- **Test Type**: INTEGRATION_TEST
- **Requirement**: Deterministic verification across all components
- **Verifiable Actions**:
  1. Execute verification multiple times with same inputs
  2. Compare outputs for consistency (no random variations)
  3. Validate results across all verification components (M20S1, M20S2, M20S3)
  4. Confirm deterministic audit trail entries

**VI-SCP-009**: Test write_success_report() Function
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: New Module
- **Test Type**: UNIT_TEST
- **Requirement**: File writing functionality
- **Verifiable Actions**:
  1. Import `write_success_report` from `scripts.checks.success_criteria_protocol`
  2. Create test report data and output path
  3. Execute function and verify file creation
  4. Validate file contains correct JSON content
  5. Test with existing file (overwrite scenario)

**VI-SCP-010**: Test Audit Trail Integration
- **Acceptance Criteria**: FR-SUCCESS_CRITERIA_PROTOCOL: All Components
- **Test Type**: UNIT_TEST
- **Requirement**: Deterministic audit trail logging
- **Verifiable Actions**:
  1. Execute `success_criteria_protocol.py` → verify audit trail entry creation
  2. Validate audit trail entry structure and content
  3. Test multiple executions create consistent audit trail entries
  4. Verify audit trail includes session ID tracking

## Test Implementation Template

```python
#!/usr/bin/env python3
"""
Verification protocol for FR-SUCCESS_CRITERIA_PROTOCOL
# {Verification IDs: VI-SCP-001, VI-SCP-002, ..., VI-SCP-010}
# {Requirement IDs: FR-SUCCESS_CRITERIA_PROTOCOL}
# {Test Type: CLI_TEST, UNIT_TEST, SCHEMA_CONTRACT, INTEGRATION_TEST}
"""

import json
import unittest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import subprocess
import hashlib
import tempfile
import os
import sys

class TestSuccessCriteriaProtocol(unittest.TestCase):
    """
    Test suite for FR-SUCCESS_CRITERIA_PROTOCOL - Success Criteria Verification Protocol Implementation
    Verifies deterministic success criteria verification protocol with automated compliance reporting.
    """
    
    def setUp(self):
        """Set up test environment for FR-SUCCESS_CRITERIA_PROTOCOL verification"""
        self.repo_root = Path.cwd()
        self.storage_data_dir = self.repo_root / "storage" / "data"
        self.scripts_dir = self.repo_root / "scripts" / "checks"
        self.success_criteria_protocol_path = self.scripts_dir / "success_criteria_protocol.py"
        
        # Ensure storage/data directory exists
        self.storage_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def run_script(self, script_path, args=None):
        """
        Run a Python script with uv and return result.
        This is a reusable helper for FR-SUCCESS_CRITERIA_PROTOCOL testing.
        """
        if args is None:
            args = []
        
        cmd = ["uv", "run", "python", str(script_path)] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result
        except FileNotFoundError:
            # This simulates when uv or python is not found
            class MockResult:
                returncode = 127
                stdout = ""
                stderr = "uv: command not found"
            return MockResult()
    
    def test_vi_scp_001_script_exists_and_executable(self):
        """VI-SCP-001: Test success_criteria_protocol.py script execution - FR-SUCCESS_CRITERIA_PROTOCOL: CLI Executable Contract"""
        # Implementation for test VI-SCP-001
        pass

    # Additional test implementations for VI-SCP-002 through VI-SCP-010

if __name__ == '__main__':
    unittest.main()
```

## Test Execution Requirements

All tests must be executed with:
1. **Python 3.8+** environment
2. **uv package manager** available
3. **storage/data/ directory** exists with write permissions
4. **Deterministic execution** without external network access
5. **Complete coverage** of all five functional requirements

## Coverage Verification

Each test in this protocol validates specific aspects of FR-SUCCESS_CRITERIA_PROTOCOL:

- **CLI Interface**: Tests exact command structure and flag usage
- **Exit Code Boundaries**: Validates all three exit code scenarios
- **Schema Contracts**: Ensures output format compliance
- **Module Exports**: Verifies all public interface components
- **Deterministic Behavior**: Ensures consistent results across runs
- **Audit Trail Integration**: Confirms logging and tracking functionality

## Acceptance Criteria Summary

All tests must pass to satisfy FR-SUCCESS_CRITERIA_PROTOCOL:
1. CLI interface accepts `--verify --output` flags correctly
2. Exit codes 0, 2, 3 are properly returned for different scenarios
3. Output JSON schema contains all required fields with correct types
4. All module exports (functions and constants) are properly defined
5. Verification results are deterministic across multiple executions
6. Audit trail integration works with consistent logging
7. All observable boundaries are properly enforced

This verification protocol ensures FR-SUCCESS_CRITERIA_PROTOCOL is fully implemented and operational.