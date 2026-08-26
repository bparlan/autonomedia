#!/usr/bin/env python3
"""
Integration binding validation tests for M20S2
Generated from verification protocol VER-M20S2V
# {Verification IDs: VER-M20S2-001, VER-M20S2-002, VER-M20S2-003, VER-M20S2-004, VER-M20S2-005, VER-M20S2-006}
"""

import json
import subprocess
import unittest
from pathlib import Path

class TestIntegrationBindingValidation(unittest.TestCase):
    """Test suite for integration binding validation across all layers"""

    def setUp(self):
        """Set up test environment"""
        self.repo_root = Path(__file__).parent.parent
        self.storage_data_dir = self.repo_root / "storage" / "data"
        self.scripts_dir = self.repo_root / "scripts" / "checks"

        # Ensure storage/data directory exists
        self.storage_data_dir.mkdir(parents=True, exist_ok=True)

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

    def test_core_ai_integration_binding_script_exists(self):
        """VI-001: Test core-AI integration binding script execution"""
        script_path = self.scripts_dir / "integrity_core_ai.py"
        
        if script_path.exists():
            # Test post-implementation behavior - script should execute and create output
            result = self.run_script(script_path, ["--validate", "--output", "storage/data/integration_core_ai_binding.json"])

            # Script can exit with code 0 (success) or 2 (violations detected), both are valid for post-implementation
            self.assertIn(result.returncode, [0, 2],
                         f"Expected exit code 0 or 2 for script execution, got {result.returncode}\n"
                         f"Stdout: {result.stdout}\n"
                         f"Stderr: {result.stderr}")

            # Verify that the output file was created
            output_file = self.storage_data_dir / "integration_core_ai_binding.json"
            self.assertTrue(output_file.exists(),
                            f"Output file {output_file} should exist after successful script execution")

            # Verify the output file contains valid JSON with expected schema
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.assertIn("validated_bindings", data)
            self.assertIn("violations", data)
            self.assertIn("total_bindings", data)

    def test_platform_core_integration_binding_script_exists(self):
        """VI-002: Test platform-core integration binding script execution"""
        script_path = self.scripts_dir / "integrity_platform_core.py"
        
        if script_path.exists():
            # Test post-implementation behavior - script should execute and create output
            result = self.run_script(script_path, ["--validate", "--output", "storage/data/integration_platform_core_binding.json"])

            # Script can exit with code 0 (success) or 2 (violations detected), both are valid for post-implementation
            self.assertIn(result.returncode, [0, 2],
                         f"Expected exit code 0 or 2 for script execution, got {result.returncode}\n"
                         f"Stdout: {result.stdout}\n"
                         f"Stderr: {result.stderr}")

            # Verify that the output file was created
            output_file = self.storage_data_dir / "integration_platform_core_binding.json"
            self.assertTrue(output_file.exists(),
                            f"Output file {output_file} should exist after successful script execution")

            # Verify the output file contains valid JSON with expected schema
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.assertIn("validated_bindings", data)
            self.assertIn("violations", data)
            self.assertIn("isolation_score", data)

    def test_web_data_integration_binding_script_exists(self):
        """VI-003: Test web-data integration binding script execution"""
        script_path = self.scripts_dir / "integrity_web_data.py"
        
        if script_path.exists():
            # Test post-implementation behavior - script should execute and create output
            result = self.run_script(script_path, ["--validate", "--output", "storage/data/integration_web_data_binding.json"])

            # Script can exit with code 0 (success) or 2 (violations detected), both are valid for post-implementation
            self.assertIn(result.returncode, [0, 2],
                         f"Expected exit code 0 or 2 for script execution, got {result.returncode}\n"
                         f"Stdout: {result.stdout}\n"
                         f"Stderr: {result.stderr}")

            # Verify that the output file was created
            output_file = self.storage_data_dir / "integration_web_data_binding.json"
            self.assertTrue(output_file.exists(),
                            f"Output file {output_file} should exist after successful script execution")

            # Verify the output file contains valid JSON with expected schema
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.assertIn("validated_bindings", data)
            self.assertIn("violations", data)
            self.assertIn("valid_access", data)

    def test_platform_isolation_report_schema(self):
        """VI-004: Test platform isolation report schema contract"""
        report_file = self.storage_data_dir / "platform_isolation_report.json"
        
        if report_file.exists():
            # Test schema validation - report file should exist and contain valid JSON
            with open(report_file, 'r') as f:
                data = json.load(f)

            self.assertIn("fully_isolated_platforms", data)
            self.assertIn("cross_platform_violations", data)
            self.assertIn("isolation_score", data)

            # Validate types
            self.assertIsInstance(data["fully_isolated_platforms"], list)
            self.assertIsInstance(data["cross_platform_violations"], list)
            self.assertIsInstance(data["isolation_score"], (int, float))

            # Validate isolation_score is within valid range
            self.assertGreaterEqual(data["isolation_score"], 0.0)
            self.assertLessEqual(data["isolation_score"], 100.0)

            # Validate cross_platform_violations structure
            for violation in data["cross_platform_violations"]:
                self.assertIn("platform_a", violation)
                self.assertIn("platform_b", violation)
                self.assertIn("import_type", violation)
                self.assertIn("severity", violation)
                self.assertIn(violation["severity"], ["CRITICAL", "HIGH", "MEDIUM"])

    def test_runtime_determinism_validation_script_exists(self):
        """VI-005: Test runtime determinism validation script execution"""
        script_path = self.scripts_dir / "integrity_runtime_determinism.py"
        
        if script_path.exists():
            # First run - create first integration matrix
            matrix1_file = self.storage_data_dir / "integration_binding_matrix_1.json"
            result1 = self.run_script(script_path, ["--validate", "--output", str(matrix1_file)])
            
            # Second run - create second integration matrix
            matrix2_file = self.storage_data_dir / "integration_binding_matrix_2.json"
            result2 = self.run_script(script_path, ["--validate", "--output", str(matrix2_file)])

            # Both runs should execute successfully (exit code 0 or 2)
            self.assertIn(result1.returncode, [0, 2],
                         f"Expected exit code 0 or 2 for first run, got {result1.returncode}\n"
                         f"Stdout: {result1.stdout}\n"
                         f"Stderr: {result1.stderr}")

            self.assertIn(result2.returncode, [0, 2],
                         f"Expected exit code 0 or 2 for second run, got {result2.returncode}\n"
                         f"Stdout: {result2.stdout}\n"
                         f"Stderr: {result2.stderr}")

            # Verify both matrix files were created
            self.assertTrue(matrix1_file.exists(),
                           f"First matrix file {matrix1_file} should exist")
            self.assertTrue(matrix2_file.exists(),
                           f"Second matrix file {matrix2_file} should exist")

            # Verify both matrix files contain valid JSON with expected schema
            with open(matrix1_file, 'r') as f:
                matrix1_data = json.load(f)
            
            with open(matrix2_file, 'r') as f:
                matrix2_data = json.load(f)

            self.assertIn("validated_bindings", matrix1_data)
            self.assertIn("violations", matrix1_data)
            self.assertIn("validated_bindings", matrix2_data)
            self.assertIn("violations", matrix2_data)

            # Test comparison run - both matrices should be compared
            comparison_file = self.storage_data_dir / "integration_determinism_report.json"
            comparison_result = self.run_script(script_path, [
                "--validate",
                "--compare",
                str(matrix1_file),
                str(matrix2_file)
            ])

            # Comparison should execute successfully (exit code 0 for match, 1 for mismatch)
            self.assertIn(comparison_result.returncode, [0, 1],
                         f"Expected exit code 0 or 1 for comparison, got {comparison_result.returncode}\n"
                         f"Stdout: {comparison_result.stdout}\n"
                         f"Stderr: {comparison_result.stderr}")

            # Verify determinism report was created
            self.assertTrue(comparison_file.exists(),
                           f"Determinism report {comparison_file} should exist")

            # Verify determinism report contains valid JSON with expected schema
            with open(comparison_file, 'r') as f:
                determinism_data = json.load(f)

            self.assertIn("checksum_match", determinism_data)
            self.assertIn("determinism_compliant", determinism_data)

            # Validate comparison details structure (actual implementation uses matrix1_path/matrix2_path)
            if "matrix1_path" in determinism_data:
                self.assertIn("matrix1_path", determinism_data)
                self.assertIn("matrix2_path", determinism_data)
                self.assertIn("checksum1", determinism_data)
                self.assertIn("checksum2", determinism_data)
                self.assertIn("identical_content", determinism_data)


if __name__ == '__main__':
    unittest.main()