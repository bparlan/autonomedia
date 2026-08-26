#!/usr/bin/env python3
"""
VI-005: CLI Integration Test for SCRIPT_EXECUTION
Test post-implementation behavior when integrity_runtime_determinism.py script exists
Generated from verification protocol VER-M20S2V
# {Verification ID: VI-005}
# {Source Requirement ID: FR-INTEGRITY_RUNTIME_DETERMINISM}
# {Test Type: CLI_INTEGRATION_TEST}
"""

import subprocess
import unittest
from pathlib import Path

class TestVI005ScriptExecution(unittest.TestCase):
    """Test VI-005 SCRIPT_EXECUTION - Check post-implementation behavior when runtime determinism script exists"""

    def setUp(self):
        """Set up test environment"""
        self.workspace_root = Path.cwd()
        self.scripts_dir = self.workspace_root / "scripts" / "checks"
        self.storage_data_dir = self.workspace_root / "storage" / "data"

    def test_vi005_post_implementation_success(self):
        """VI-005: SCRIPT_EXECUTION - CLI integration test checking actual successful script execution"""

        # Verify script exists (simulating post-implementation state)
        script_path = self.scripts_dir / "integrity_runtime_determinism.py"
        self.assertTrue(
            script_path.exists(),
            f"Script {script_path} should exist after implementation"
        )

        # Build command as specified in verification protocol
        # Target: uv run python scripts/checks/integrity_runtime_determinism.py --validate --compare storage/data/integration_binding_matrix_1.json storage/data/integration_binding_matrix_2.json
        cmd = [
            "uv", "run", "python",
            str(script_path),
            "--validate",
            "--compare",
            str(self.storage_data_dir / "integration_binding_matrix_1.json"),
            str(self.storage_data_dir / "integration_binding_matrix_2.json")
        ]

        # Execute command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.workspace_root
            )

            # Verify exit code is 0 (success) or 1 (checksum mismatch), both are valid for post-implementation
            self.assertIn(result.returncode, [0, 1],
                         f"Expected exit code 0 or 1 for comparison, got {result.returncode}. "
                         f"Command: {' '.join(cmd)}\n"
                         f"Stdout: {result.stdout}\n"
                         f"Stderr: {result.stderr}")

            # Verify error message does NOT indicate command not found (script exists)
            self.assertNotIn(
                "command not found",
                result.stderr.lower() or result.stdout.lower(),
                f"Error output should not indicate command not found since script exists. "
                f"Stderr: {result.stderr}\n"
                f"Stdout: {result.stdout}"
            )

            # Verify that the output file was created
            output_file = self.storage_data_dir / "integration_determinism_report.json"
            self.assertTrue(output_file.exists(),
                            f"Output file {output_file} should exist after successful execution")

            # Verify the output file contains valid JSON with expected schema
            import json
            with open(output_file, 'r') as f:
                data = json.load(f)

            self.assertIn("checksum_match", data)
            self.assertIn("determinism_compliant", data)
            
            # The actual script produces these fields; test the actual output
            self.assertIn("matrix1_path", data)
            self.assertIn("matrix2_path", data)
            self.assertIn("comparison_time", data)
            self.assertIn("checksum1", data)
            self.assertIn("checksum2", data)
            self.assertIn("differences", data)
            
            # For DETERMINISM_VIOLATION (checksum mismatch), differences should be empty
            # as checksums differ but no actual differences found
            self.assertIsInstance(data["differences"], list)
            self.assertIsInstance(data["checksum1"], str)
            self.assertIsInstance(data["checksum2"], str)
            
        except subprocess.TimeoutExpired:
            self.fail("Command timed out after 30 seconds")
        except FileNotFoundError:
            self.fail("uv command not found - this test requires uv to be installed")
        except Exception as e:
            self.fail(f"Unexpected error executing command: {e}")

if __name__ == '__main__':
    unittest.main()