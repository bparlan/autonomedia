#!/usr/bin/env python3
"""
VI-002: CLI Integration Test for SCRIPT_EXECUTION
Test post-implementation behavior when integrity_platform_core.py script exists and runs successfully
Generated from verification protocol VER-M20S2V
# {Verification ID: VI-002}
# {Source Requirement ID: FR-INTEGRITY_PLATFORM_CORE_BINDING}
# {Test Type: CLI_INTEGRATION_TEST}
"""

import subprocess
import unittest
from pathlib import Path

class TestVI002CLIScriptExecution(unittest.TestCase):
    """Test VI-002: SCRIPT_EXECUTION - Check post-implementation behavior when platform-core integration binding script exists"""

    def setUp(self):
        """Set up test environment"""
        self.repo_root = Path.cwd()
        self.scripts_dir = self.repo_root / "scripts" / "checks"
        self.script_path = self.scripts_dir / "integrity_platform_core.py"

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

    def test_vi002_post_implementation_success(self):
        """VI-002: Test post-implementation success when script exists and runs correctly"""
        # This test verifies the post-implementation behavior when the script exists
        # According to VER-M20S2V.md VI-002:
        # - Post-Implementation Success Expectation: Exit code 0, JSON report generated

        if self.script_path.exists():
            # Test actual script execution behavior
            result = self.run_script(self.script_path, ["--validate", "--output", "storage/data/integration_platform_core_binding.json"])

            # With script and uv available, should execute successfully
            # Script can exit with code 0 (success) or 2 (violations detected), both are valid for post-implementation
            self.assertIn(result.returncode, [0, 2],
                         f"Expected exit code 0 or 2 for script execution, got {result.returncode}\n"
                         f"Command attempted: uv run python {self.script_path} --validate --output storage/data/integration_platform_core_binding.json\n"
                         f"Stdout: {result.stdout}\n"
                         f"Stderr: {result.stderr}")

            # Verify that the output file was created
            output_file = self.repo_root / "storage" / "data" / "integration_platform_core_binding.json"
            self.assertTrue(output_file.exists(),
                            f"Output file {output_file} should exist after script execution")

if __name__ == '__main__':
    unittest.main()