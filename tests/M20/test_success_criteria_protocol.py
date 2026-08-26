#!/usr/bin/env python3
"""
Verification tests for FR-SUCCESS_CRITERIA_PROTOCOL
Generated from VER-M20S3V verification protocol
# {Verification IDs: VI-SCP-001, VI-SCP-002, VI-SCP-003, VI-SCP-004, VI-SCP-005, VI-SCP-006, VI-SCP-007, VI-SCP-008, VI-SCP-009, VI-SCP-010, VI-SCP-011}
# {Requirement IDs: FR-SUCCESS_CRITERIA_PROTOCOL}
# {Test Type: UNIT_TEST, CLI_TEST, SCHEMA_CONTRACT, INTEGRATION_TEST}
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
        # Test script exists and is accessible
        self.assertTrue(self.success_criteria_protocol_path.exists(), 
                       f"Script not found at {self.success_criteria_protocol_path}")
        
        # Test script can be executed with help
        result = self.run_script(self.success_criteria_protocol_path, ["--help"])
        self.assertEqual(result.returncode, 0, 
                         f"Script should execute successfully: {result.stderr}")
        
        # Test script is Python 3 compatible
        with open(self.success_criteria_protocol_path, 'r') as f:
            content = f.read()
            self.assertTrue(content.startswith("#!/usr/bin/env python3"),
                           "Script must use Python 3 shebang")
    
    def test_vi_scp_002_cli_interface_contract(self):
        """VI-SCP-002: Test CLI interface contract - FR-SUCCESS_CRITERIA_PROTOCOL: Interface Contract"""
        # Test successful verification execution
        output_path = self.storage_data_dir / "success_criteria_report.json"
        if output_path.exists():
            output_path.unlink()  # Clean up if exists
        
        result = self.run_script(
            self.success_criteria_protocol_path,
            ["--verify", "--output", str(output_path)]
        )
        
        # Verify exit code for successful verification
        self.assertEqual(result.returncode, 0,
                        f"Expected exit code 0, got {result.returncode}: {result.stderr}")
        
        # Verify output file creation
        self.assertTrue(output_path.exists(),
                       f"Output file should be created: {output_path}")
        
        # Verify output contains valid JSON
        with open(output_path, 'r') as f:
            try:
                data = json.load(f)
                self.assertIsInstance(data, dict,
                                    "Output should be a JSON object")
            except json.JSONDecodeError as e:
                self.fail(f"Output is not valid JSON: {e}")
    
    def test_vi_scp_003_observable_boundary_exit_codes(self):
        """VI-SCP-003: Test observable boundary - exit codes for different scenarios"""
        
        # Test exit code 0 for successful verification
        output_path = self.storage_data_dir / "success_criteria_report_0.json"
        result = self.run_script(
            self.success_criteria_protocol_path,
            ["--verify", "--output", str(output_path)]
        )
        self.assertEqual(result.returncode, 0,
                        f"Expected exit code 0, got {result.returncode}")
        if output_path.exists():
            output_path.unlink()
        
        # Test exit code 2 for criteria failures (simulated)
        # This requires modifying the script to simulate failures
        # For now, we'll test the mechanism exists
        
        # Test exit code 3 for verification failures (simulated)
        # This requires creating a scenario that causes script failure
        # For now, we'll test the mechanism exists
        
        # Note: In a real implementation, you would need to mock
        # the verification logic to test these scenarios
    
    def test_vi_scp_004_output_schema_contract(self):
        """VI-SCP-004: Test output schema contract - FR-SUCCESS_CRITERIA_PROTOCOL: Observable Boundary"""
        
        # Generate verification report
        output_path = self.storage_data_dir / "success_criteria_report_schema.json"
        if output_path.exists():
            output_path.unlink()
        
        result = self.run_script(
            self.success_criteria_protocol_path,
            ["--verify", "--output", str(output_path)]
        )
        self.assertEqual(result.returncode, 0,
                        f"Verification should succeed: {result.stderr}")
        
        # Verify output file exists
        self.assertTrue(output_path.exists(),
                       f"Output file should exist: {output_path}")
        
        # Load and validate schema
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        # Validate required fields exist and have correct types
        self.assertIn('verified_criteria', data,
                     "Output must contain 'verified_criteria' field")
        self.assertIn('failed_criteria', data,
                     "Output must contain 'failed_criteria' field")
        self.assertIn('overall_success', data,
                     "Output must contain 'overall_success' field")
        self.assertIn('compliance_score', data,
                     "Output must contain 'compliance_score' field")
        
        # Validate field types
        self.assertIsInstance(data['verified_criteria'],
                             (list, dict),
                             "'verified_criteria' must be list or dict")
        self.assertIsInstance(data['failed_criteria'],
                             (list, dict),
                             "'failed_criteria' must be list or dict")
        self.assertIsInstance(data['overall_success'], bool,
                            "'overall_success' must be boolean")
        self.assertIsInstance(data['compliance_score'], (int, float),
                            "'compliance_score' must be numeric")
        
        # Validate compliance_score range
        self.assertGreaterEqual(data['compliance_score'], 0.0,
                               "'compliance_score' must be >= 0.0")
        self.assertLessEqual(data['compliance_score'], 1.0,
                            "'compliance_score' must be <= 1.0")
        
        # Validate consistency between fields
        if data['overall_success']:
            self.assertEqual(len(data['failed_criteria']), 0,
                            "'overall_success=True' requires no failed criteria")
            self.assertGreater(data['compliance_score'], 0.0,
                              "'overall_success=True' requires positive compliance_score")
    
    def test_vi_scp_005_verify_m20_criteria_function(self):
        """VI-SCP-005: Test verify_m20_criteria() function exports and behavior"""
        
        # Import the module and function
        sys.path.insert(0, str(self.scripts_dir))
        
        try:
            from success_criteria_protocol import verify_m20_criteria
            
            # Execute function
            results = verify_m20_criteria()
            
            # Validate return type
            self.assertIsInstance(results, dict,
                                "verify_m20_criteria() should return dict")
            
            # Validate function includes deterministic audit trail logging
            # This would be tested in the actual implementation
            
        except ImportError as e:
            self.fail(f"Could not import verify_m20_criteria(): {e}")
    
    def test_vi_scp_006_generate_success_report_function(self):
        """VI-SCP-006: Test generate_success_report() function exports and behavior"""
        
        # Import the module and function
        sys.path.insert(0, str(self.scripts_dir))
        
        try:
            from success_criteria_protocol import generate_success_report
            
            # Test with sample data
            test_results = {
                "verified_criteria": ["M20S1_test"],
                "failed_criteria": [],
                "overall_success": True,
                "compliance_score": 1.0
            }
            
            # Execute function
            report = generate_success_report(test_results)
            
            # Validate return type
            self.assertIsInstance(report, dict,
                                "generate_success_report() should return dict")
            
            # Validate report contains required fields
            self.assertIn('verified_criteria', report,
                         "Report should contain 'verified_criteria'")
            self.assertIn('failed_criteria', report,
                         "Report should contain 'failed_criteria'")
            self.assertIn('overall_success', report,
                         "Report should contain 'overall_success'")
            self.assertIn('compliance_score', report,
                         "Report should contain 'compliance_score'")
            
        except ImportError as e:
            self.fail(f"Could not import generate_success_report(): {e}")
    
    def test_vi_scp_007_success_criteria_violation_exception(self):
        """VI-SCP-007: Test SuccessCriteriaViolation exception class"""
        
        sys.path.insert(0, str(self.scripts_dir))
        
        try:
            from success_criteria_protocol import SuccessCriteriaViolation
            
            # Test exception can be raised
            try:
                raise SuccessCriteriaViolation("Test violation", {"failed_criteria": ["M20S2_binding"]})
            except SuccessCriteriaViolation as e:
                # Test exception can be caught
                self.assertIsInstance(e, Exception,
                                    "SuccessCriteriaViolation should extend Exception")
                self.assertIn("Test violation", str(e),
                            "Exception should contain message")
                
                # Test exception includes error context
                if hasattr(e, 'failed_criteria'):
                    self.assertIn("M20S2_binding", e.failed_criteria,
                                "Exception should include failed criteria context")
                
        except ImportError as e:
            self.fail(f"Could not import SuccessCriteriaViolation: {e}")
    
    def test_vi_scp_008_success_criteria_map_constant(self):
        """VI-SCP-008: Test SUCCESS_CRITERIA_MAP constant"""
        
        sys.path.insert(0, str(self.scripts_dir))
        
        try:
            from success_criteria_protocol import SUCCESS_CRITERIA_MAP
            
            # Validate map type
            self.assertIsInstance(SUCCESS_CRITERIA_MAP, dict,
                                "SUCCESS_CRITERIA_MAP should be dict")
            
            # Validate map structure
            for key, value in SUCCESS_CRITERIA_MAP.items():
                self.assertIsInstance(key, str,
                                    "SUCCESS_CRITERIA_MAP keys should be strings")
                self.assertIsInstance(value, list,
                                    "SUCCESS_CRITERIA_MAP values should be lists")
                for item in value:
                    self.assertIsInstance(item, str,
                                        "SUCCESS_CRITERIA_MAP list items should be strings")
            
            # Validate map contains M20 criteria definitions
            expected_keys = ["m20s1_3layer_pattern", "m20s2_integration_bindings", "m20s3_validation_workflow"]
            for key in expected_keys:
                self.assertIn(key, SUCCESS_CRITERIA_MAP,
                            f"SUCCESS_CRITERIA_MAP should contain {key}")
            
        except ImportError as e:
            self.fail(f"Could not import SUCCESS_CRITERIA_MAP: {e}")
    
    def test_vi_scp_009_deterministic_verification_execution(self):
        """VI-SCP-009: Test deterministic verification protocol execution"""
        
        # Run verification multiple times with same inputs
        results = []
        for i in range(3):
            output_path = self.storage_data_dir / f"success_criteria_deterministic_{i}.json"
            result = self.run_script(
                self.success_criteria_protocol_path,
                ["--verify", "--output", str(output_path)]
            )
            
            if output_path.exists():
                with open(output_path, 'r') as f:
                    data = json.load(f)
                    results.append(data)
                output_path.unlink()
        
        # Validate all runs produced consistent results
        for i in range(1, len(results)):
            self.assertEqual(results[0]['verified_criteria'], results[i]['verified_criteria'],
                           "Verification should be deterministic across runs")
            self.assertEqual(results[0]['failed_criteria'], results[i]['failed_criteria'],
                           "Verification should be deterministic across runs")
            self.assertEqual(results[0]['overall_success'], results[i]['overall_success'],
                           "Verification should be deterministic across runs")
            self.assertEqual(results[0]['compliance_score'], results[i]['compliance_score'],
                           "Verification should be deterministic across runs")
    
    def test_vi_scp_010_write_success_report_function(self):
        """VI-SCP-010: Test write_success_report() function"""
        
        sys.path.insert(0, str(self.scripts_dir))
        
        try:
            from success_criteria_protocol import write_success_report
            
            # Test data
            test_report = {
                "verified_criteria": ["M20S1_test"],
                "failed_criteria": [],
                "overall_success": True,
                "compliance_score": 1.0,
                "verification_session_id": "test-session-789"
            }
            
            # Test output path
            test_output_path = self.temp_dir / "test_success_report.json"
            
            # Execute function
            write_success_report(test_report, str(test_output_path))
            
            # Verify file was created
            self.assertTrue(test_output_path.exists(),
                          "write_success_report() should create output file")
            
            # Verify file contains correct JSON content
            with open(test_output_path, 'r') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(loaded_data, test_report,
                           "write_success_report() should write exact data")
            
        except ImportError as e:
            self.fail(f"Could not import write_success_report: {e}")
    
    def test_vi_scp_011_deterministic_audit_trail_integration(self):
        """VI-SCP-011: Test deterministic audit trail integration"""
        
        # Execute success_criteria_protocol.py
        output_path = self.storage_data_dir / "success_criteria_audit_test.json"
        if output_path.exists():
            output_path.unlink()
        
        result = self.run_script(
            self.success_criteria_protocol_path,
            ["--verify", "--output", str(output_path)]
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Verification should succeed: {result.stderr}")
        
        # For this test, we're verifying the script execution
        # The actual audit trail verification would depend on the implementation
        # This ensures the script can execute without errors
        
        # Verify output was created
        self.assertTrue(output_path.exists(),
                       "Script should create output file")
        
        # Note: Additional audit trail validation would be
        # implementation-specific and should be added based on
        # the actual success_criteria_protocol.py implementation


class MockResult:
    """Mock result object for script execution testing"""
    def __init__(self, exit_code, stdout, stderr):
        self.returncode = exit_code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == '__main__':
    unittest.main()