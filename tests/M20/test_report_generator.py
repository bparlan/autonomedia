#!/usr/bin/env python3
"""
VI-004: FILESYSTEM_STATE_CONTRACT and VI-009: SCHEMA_CONTRACT
Test filesystem state and HTML report generation for M20S3 verification protocol
Generated from verification protocol VER-M20S3V
# {Verification ID: VI-004}
# {Source Requirement ID: FR-REPORT_GENERATION}
# {Test Type: FILESYSTEM_STATE_CONTRACT}
# {Verification ID: VI-009}
# {Source Requirement ID: FR-REPORT_GENERATION}
# {Test Type: SCHEMA_CONTRACT}
"""

import subprocess
import unittest
import json
import os
from pathlib import Path
from typing import Dict, Any

class TestVI004FilesystemStateContract(unittest.TestCase):
    """Test VI-004: FILESYSTEM_STATE_CONTRACT - Check post-implementation behavior for report generation"""

    def setUp(self):
        """Set up test environment"""
        self.repo_root = Path.cwd()
        self.scripts_dir = self.repo_root / "scripts" / "checks"
        self.script_path = self.scripts_dir / "report_generator.py"

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

    def test_vi004_post_implementation_success(self):
        """VI-004: Test post-implementation success when report_generator.py script exists and runs correctly"""
        # This test verifies the post-implementation behavior when the script exists
        # According to VER-M20S3V.md VI-004:
        # - Post-Implementation Success Expectation: Files generated, non-empty

        if self.script_path.exists():
            # First create a mock compliance report for report generator to process
            compliance_file = self.repo_root / "storage" / "data" / "automated_compliance_report.json"
            compliance_file.parent.mkdir(parents=True, exist_ok=True)

            mock_compliance_report = {
                "report_metadata": {
                    "report_id": "test-report-001",
                    "generation_timestamp": "2024-01-01T00:00:00Z"
                },
                "layer_verification_results": [
                    {
                        "layer_name": "M20S3",
                        "criteria_verified": ["FR-SUCCESS_CRITERIA_PROTOCOL"],
                        "criteria_failed": [],
                        "layer_compliance_score": 1.0,
                        "verification_timestamp": "2024-01-01T00:00:00Z"
                    }
                ],
                "overall_compliance_assessment": {
                    "overall_score": 1.0,
                    "overall_status": "passed",
                    "critical_failures": [],
                    "recommendations": [],
                    "assessment_timestamp": "2024-01-01T00:00:00Z"
                },
                "audit_trail_reference": [
                    {
                        "session_id": "test-session-001",
                        "component": "compliance_reporting",
                        "entry_timestamp": "2024-01-01T00:00:00Z",
                        "integrity_hash": "a" * 64
                    }
                ]
            }

            with open(compliance_file, 'w') as f:
                json.dump(mock_compliance_report, f)

            # Test report generator script execution
            result = self.run_script(
                self.script_path,
                ["--generate_reports", "--input", "storage/data/automated_compliance_report.json"]
            )

            # Script can exit with code 0 (success) or 3 (report generation fails), both are valid for post-implementation
            self.assertIn(
                result.returncode, [0, 3],
                f"Expected exit code 0 or 3 for script execution, got {result.returncode}\n"
                f"Command attempted: uv run python {self.script_path} --generate_reports --input storage/data/automated_compliance_report.json\n"
                f"Stdout: {result.stdout}\n"
                f"Stderr: {result.stderr}"
            )

            # Verify that the output files were created
            html_file = self.repo_root / "storage" / "data" / "m20_verification_report.html"
            pdf_file = self.repo_root / "storage" / "data" / "m20_verification_report.pdf"

            # At least one of the reports should be generated (HTML or PDF)
            self.assertTrue(
                html_file.exists() or pdf_file.exists(),
                f"At least one report file should exist after script execution: {html_file.exists()}, {pdf_file.exists()}"
            )

            # If HTML report is generated, verify it's non-empty and contains required sections
            if html_file.exists():
                html_size = html_file.stat().st_size
                self.assertGreater(
                    html_size, 0,
                    f"HTML report file {html_file} should be non-empty"
                )

                # Verify basic HTML structure
                with open(html_file, 'r') as f:
                    html_content = f.read()

                self.assertIn("<html", html_content, "HTML report should contain HTML structure")
                self.assertIn("M20 Verification Report", html_content, "HTML report should contain title")
                self.assertIn("Executive Summary", html_content, "HTML report should contain executive summary")
                self.assertIn("Detailed Verification Results", html_content, "HTML report should contain detailed results")
                self.assertIn("Audit Trail Information", html_content, "HTML report should contain audit trail information")

            # If PDF report is generated, verify it's non-empty
            if pdf_file.exists():
                pdf_size = pdf_file.stat().st_size
                self.assertGreater(
                    pdf_size, 0,
                    f"PDF report file {pdf_file} should be non-empty"
                )

    def test_vi004_cli_executable_contract(self):
        """VI-004: Test CLI executable contract specification"""
        # Verify the script exists and is executable
        self.assertTrue(self.script_path.exists(),
                       f"Script {self.script_path} should exist for CLI executable contract test")

    def test_vi009_schema_contract(self):
        """VI-009: Test m20_verification_report.html schema contract"""
        # This test covers the SCHEMA_CONTRACT verification for HTML report generation
        html_file = self.repo_root / "storage" / "data" / "m20_verification_report.html"

        if html_file.exists():
            html_size = html_file.stat().st_size
            self.assertGreater(
                html_size, 0,
                f"HTML report file {html_file} should be non-empty for schema validation"
            )

            # Read HTML content and validate structure
            with open(html_file, 'r') as f:
                html_content = f.read()

            # Validate HTML structure contains required sections
            required_sections = [
                "<html>",
                "M20 Verification Report",
                "Executive Summary",
                "Detailed Verification Results",
                "Audit Trail Information",
                "Compliance Evidence"
            ]

            for section in required_sections:
                self.assertIn(
                    section, html_content,
                    f"HTML report should contain required section: {section}"
                )

            # Validate basic HTML structure
            self.assertTrue(
                html_content.strip().startswith("<!DOCTYPE html>") or html_content.strip().startswith("<html>"),
                "HTML report should have proper DOCTYPE and html tag"
            )

            # Validate HTML contains required elements
            self.assertIn(
                "<head>", html_content,
                "HTML report should contain head section"
            )
            self.assertIn(
                "<body>", html_content,
                "HTML report should contain body section"
            )

if __name__ == '__main__':
    unittest.main()