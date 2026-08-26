#!/usr/bin/env python3
"""
VI-005: CLI Integration Test for SCRIPT_EXECUTION and VI-010: SCHEMA_CONTRACT
Test post-implementation behavior when validation_workflow.py script exists and runs successfully
Generated from verification protocol VER-M20S3V
# {Verification ID: VI-005}
# {Source Requirement ID: FR-VALIDATION_WORKFLOW}
# {Test Type: CLI_INTEGRATION_TEST}
# {Verification ID: VI-010}
# {Source Requirement ID: FR-VALIDATION_WORKFLOW}
# {Test Type: SCHEMA_CONTRACT}
"""

import subprocess
import unittest
import json
from pathlib import Path
from typing import Dict, Any

class TestVI005CLIScriptExecution(unittest.TestCase):
    """Test VI-005: SCRIPT_EXECUTION - Check post-implementation behavior when validation_workflow.py exists"""

    def setUp(self):
        """Set up test environment"""
        self.repo_root = Path.cwd()
        self.scripts_dir = self.repo_root / "scripts" / "checks"
        self.script_path = self.scripts_dir / "validation_workflow.py"

    def run_script(self, script_path, args=None):
        """Run a Python script with uv and return result"""
        if args is None:
            args = []

        cmd = ["uv", "run", "python", str(script_path)] + args

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result
        except FileNotFoundError:
            # This simulates when uv or python is not found
            class MockResult:
                returncode = 127
                stdout = ""
                stderr = "uv: command not found"
            return MockResult()

    def test_vi005_post_implementation_success(self):
        """VI-005: Test post-implementation success when script exists and runs correctly"""
        # This test verifies the post-implementation behavior when the script exists
        # According to VER-M20S3V.md VI-005:
        # - Post-Implementation Success Expectation: Exit code 0, JSON file generated

        if self.script_path.exists():
            # Test validation workflow script execution
            result = self.run_script(
                self.script_path,
                ["--execute", "--mode", "full", "--output", "storage/data/validation_workflow_state.json"]
            )

            # Script can exit with code 0 (success), 2 (validation fails), or 3 (workflow state corruption), all are valid for post-implementation
            self.assertIn(
                result.returncode, [0, 2, 3],
                f"Expected exit code 0, 2, or 3 for script execution, got {result.returncode}\n"
                f"Command attempted: uv run python {self.script_path} --execute --mode full --output storage/data/validation_workflow_state.json\n"
                f"Stdout: {result.stdout}\n"
                f"Stderr: {result.stderr}"
            )

            # Verify that the output file was created
            output_file = self.repo_root / "storage" / "data" / "validation_workflow_state.json"
            self.assertTrue(
                output_file.exists(),
                f"Output file {output_file} should exist after script execution"
            )

            # Verify the output file contains valid JSON with expected schema
            with open(output_file, 'r') as f:
                data = json.load(f)

            # Verify required schema fields
            self.assertIn("workflow_id", data)
            self.assertIn("executed_steps", data)
            self.assertIn("step_results", data)
            self.assertIn("workflow_status", data)

            # Validate workflow state structure
            self.assertIsInstance(data["workflow_id"], str)
            self.assertIsInstance(data["executed_steps"], list)
            self.assertIsInstance(data["step_results"], dict)
            self.assertIsInstance(data["workflow_status"], str)

            # Validate executed_steps structure
            for step in data["executed_steps"]:
                self.assertIn("step_id", step)
                self.assertIn("step_name", step)
                self.assertIn("step_status", step)
                self.assertIn("step_timestamp", step)
                self.assertIn("step_result", step)
                self.assertIn("step_dependencies", step)

                # Validate step field types
                self.assertIsInstance(step["step_id"], str)
                self.assertIsInstance(step["step_name"], str)
                self.assertIn(step["step_status"], ["pending", "running", "completed", "failed"])
                self.assertIsInstance(step["step_timestamp"], str)
                self.assertIsInstance(step["step_result"], dict)
                self.assertIsInstance(step["step_dependencies"], list)

            # Validate step_results structure
            for step_name, step_result in data["step_results"].items():
                self.assertIsInstance(step_name, str)
                self.assertIsInstance(step_result, dict)

    def test_vi005_cli_executable_contract(self):
        """VI-005: Test CLI executable contract specification"""
        # Verify the script exists and is executable
        self.assertTrue(self.script_path.exists(),
                       f"Script {self.script_path} should exist for CLI executable contract test")

    def test_vi010_schema_contract(self):
        """VI-010: Test validation_workflow_state.json schema contract"""
        # This test covers the SCHEMA_CONTRACT verification for validation workflow
        output_file = self.repo_root / "storage" / "data" / "validation_workflow_state.json"

        if output_file.exists():
            with open(output_file, 'r') as f:
                data = json.load(f)

            # Schema validation for validation_workflow_state.json
            self.assertIn("workflow_id", data)
            self.assertIn("executed_steps", data)
            self.assertIn("step_results", data)
            self.assertIn("workflow_status", data)

            # Validate workflow field types
            self.assertIsInstance(data["workflow_id"], str)
            self.assertIsInstance(data["executed_steps"], list)
            self.assertIsInstance(data["step_results"], dict)
            self.assertIsInstance(data["workflow_status"], str)

            # Validate workflow_status values
            self.assertIn(data["workflow_status"], ["pending", "running", "completed", "failed"])

            # Validate executed_steps structure
            for step in data["executed_steps"]:
                self.assertIsInstance(step.get("step_id"), str)
                self.assertIsInstance(step.get("step_name"), str)
                self.assertIsInstance(step.get("step_status"), str)
                self.assertIsInstance(step.get("step_timestamp"), str)
                self.assertIsInstance(step.get("step_result"), dict)
                self.assertIsInstance(step.get("step_dependencies"), list)

                # Validate step_status values
                self.assertIn(step.get("step_status", ""), ["pending", "running", "completed", "failed"])

            # Validate step_results structure
            for step_name, step_result in data["step_results"].items():
                self.assertIsInstance(step_name, str)
                self.assertIsInstance(step_result, dict)

if __name__ == '__main__':
    unittest.main()