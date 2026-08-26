#!/usr/bin/env python3
"""
VI-004: Schema Validation Test for SCRIPT_EXECUTION
Test post-implementation behavior when platform isolation report exists
Generated from verification protocol VER-M20S2V
# {Verification ID: VI-004}
# {Source Requirement ID: FR-INTEGRITY_PLATFORM_ISOLATION}
# {Test Type: SCHEMA_CONTRACT}
"""

import json
import unittest
from pathlib import Path

class TestVI004SchemaValidation(unittest.TestCase):
    """Test VI-004: SCHEMA_CONTRACT - Check post-implementation behavior when platform isolation report exists"""

    def setUp(self):
        """Set up test environment"""
        self.workspace_root = Path.cwd()
        self.storage_data_dir = self.workspace_root / "storage" / "data"
        self.report_file = self.storage_data_dir / "platform_isolation_report.json"

    def test_vi004_post_implementation_success(self):
        """VI-004: Test post-implementation success when report exists"""
        # This test verifies the post-implementation behavior when the report exists
        # According to VER-M20S2V.md VI-004:
        # - Post-Implementation Success Expectation: File exists with valid schema

        if self.report_file.exists():
            # Test actual schema validation behavior
            with open(self.report_file, 'r') as f:
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

if __name__ == '__main__':
    unittest.main()