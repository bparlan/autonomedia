#!/usr/bin/env python3
"""
VI-003: CLI Integration Test for SCRIPT_EXECUTION
Test post-implementation behavior when integrity_web_data.py script exists and runs successfully
Generated from verification protocol VER-M20S2V
# {Verification ID: VI-003}
# {Source Requirement ID: FR-INTEGRITY_WEB_DATA_BINDING}
# {Test Type: CLI_INTEGRATION_TEST}
"""

import subprocess
import unittest
from pathlib import Path

class TestVI003ScriptExecution(unittest.TestCase):
    """Test VI-003 SCRIPT_EXECUTION - Check post-implementation behavior when web-data integration binding script exists"""

    def setUp(self):
        """Set up test environment"""
        self.workspace_root = Path.cwd()
        self.scripts_dir = self.workspace_root / "scripts" / "checks"
        self.storage_data_dir = self.workspace_root / "storage" / "data"

    def test_vi003_post_implementation_success(self):
        """VI-003: SCRIPT_EXECUTION - CLI integration test checking actual successful script execution"""

        # Verify script exists (simulating post-implementation state)
        script_path = self.scripts_dir / "integrity_web_data.py"
        self.assertTrue(
            script_path.exists(),
            f"Script {script_path} should exist after implementation"
        )

        # Build command as specified in verification protocol
        # Target: uv run python scripts/checks/integrity_web_data.py --validate --output storage/data/integration_web_data_binding.json
        cmd = [
            "uv", "run", "python",
            str(script_path),
            "--validate",
            "--output",
            str(self.storage_data_dir / "integration_web_data_binding.json")
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

            # Verify exit code is 0 (success) or 2 (violations detected), both are valid for post-implementation
            self.assertIn(result.returncode, [0, 2],
                         f"Expected exit code 0 or 2 (success or violations), got {result.returncode}. "
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
            output_file = self.storage_data_dir / "integration_web_data_binding.json"
            self.assertTrue(output_file.exists(),
                            f"Output file {output_file} should exist after successful execution")

            # Verify the output file contains valid JSON with expected schema
            import json
            with open(output_file, 'r') as f:
                data = json.load(f)

            self.assertIn("validated_bindings", data)
            self.assertIn("violations", data)
            self.assertIn("valid_access", data)

        except subprocess.TimeoutExpired:
            self.fail("Command timed out after 30 seconds")
        except FileNotFoundError:
            self.fail("uv command not found - this test requires uv to be installed")
        except Exception as e:
            self.fail(f"Unexpected error executing command: {e}")

if __name__ == '__main__':
    unittest.main()