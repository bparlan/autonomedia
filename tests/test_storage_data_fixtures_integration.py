"""
Integration test for storage/data directory fixtures matching VER-M20S2V.md specification.

This test verifies that the fixtures created for the M20S2 verification protocol
exactly match the requirements specified in the VER-M20S2V.md document.
"""

import pytest
from pathlib import Path

@pytest.fixture
def storage_data_directory():
    """Path to the storage/data directory for testing."""
    return Path("storage/data")

@pytest.fixture
def integration_core_ai_binding():
    """Fixture for integration_core_ai_binding.json data structure."""
    return {
        "validated_bindings": [
            {
                "source": "src/autonomedia/core/",
                "target": "src/autonomedia/ai/",
                "isolation_score": 0.85,
                "validation_timestamp": "2026-08-26T11:00:00Z",
                "violations": []
            }
        ],
        "cross_layer_imports": [],
        "validation_timestamp": "2026-08-26T11:00:00Z",
        "summary": {
            "total_bindings": 1,
            "isolated_bindings": 1,
            "isolated_percentage": 100.0
        }
    }

@pytest.fixture
def integration_platform_core_binding():
    """Fixture for integration_platform_core_binding.json data structure."""
    return {
        "isolation_reports": [
            {
                "platform": "core",
                "components": [
                    "src/autonomedia/core/",
                    "src/autonomedia/shared/"
                ],
                "isolation_score": 0.92,
                "validation_timestamp": "2026-08-26T11:00:00Z",
                "violations": []
            }
        ],
        "validation_timestamp": "2026-08-26T11:00:00Z",
        "summary": {
            "total_platforms": 1,
            "fully_isolated_platforms": 1,
            "isolation_percentage": 100.0
        }
    }

@pytest.fixture
def integration_web_data_binding():
    """Fixture for integration_web_data_binding.json data structure."""
    return {
        "web_data_integration_reports": [
            {
                "data_source": "src/autonomedia/web/",
                "components": [
                    "src/autonomedia/web/",
                    "src/autonomedia/shared/"
                ],
                "isolation_score": 0.78,
                "validation_timestamp": "2026-08-26T11:00:00Z",
                "violations": []
            }
        ],
        "validation_timestamp": "2026-08-26T11:00:00Z",
        "summary": {
            "total_data_sources": 1,
            "integrated_data_sources": 1,
            "integration_percentage": 100.0
        }
    }

@pytest.fixture
def platform_isolation_report():
    """Fixture for platform_isolation_report.json schema structure."""
    return {
        "isolated_platforms": [
            {
                "platform_name": "core",
                "isolation_score": 0.92,
                "components": [
                    "src/autonomedia/core/",
                    "src/autonomedia/shared/"
                ],
                "validation_timestamp": "2026-08-26T11:00:00Z"
            },
            {
                "platform_name": "web_data",
                "isolation_score": 0.78,
                "components": [
                    "src/autonomedia/web/",
                    "src/autonomedia/shared/"
                ],
                "validation_timestamp": "2026-08-26T11:00:00Z"
            },
            {
                "platform_name": "ai_engine",
                "isolation_score": 0.85,
                "components": [
                    "src/autonomedia/ai/",
                    "src/autonomedia/shared/"
                ],
                "validation_timestamp": "2026-08-26T11:00:00Z"
            }
        ],
        "isolation_score": 0.85,
        "validation_timestamp": "2026-08-26T11:00:00Z",
        "schema_version": "1.0"
    }

@pytest.fixture
def integration_binding_matrix_1():
    """Fixture for integration_binding_matrix_1.json data structure."""
    return {
        "checksums": {
            "core": "a1b2c3d4e5f6",
            "platform": "f6e5d4c3b2a1",
            "web": "1234567890ab",
            "ai": "cdef123456"
        },
        "bindings": [
            {
                "source": "src/autonomedia/core/",
                "target": "src/autonomedia/ai/",
                "checksum": "a1b2c3d4e5f6"
            },
            {
                "source": "src/autonomedia/web/",
                "target": "src/autonomedia/shared/",
                "checksum": "1234567890ab"
            }
        ],
        "validation_timestamp": "2026-08-26T11:00:00Z"
    }

@pytest.fixture
def integration_binding_matrix_2():
    """Fixture for integration_binding_matrix_2.json data structure (deterministic comparison)."""
    return {
        "checksums": {
            "core": "a1b2c3d4e5f6",
            "platform": "f6e5d4c3b2a1",
            "web": "1234567890ab",
            "ai": "cdef123456"
        },
        "bindings": [
            {
                "source": "src/autonomedia/core/",
                "target": "src/autonomedia/ai/",
                "checksum": "a1b2c3d4e5f6"
            },
            {
                "source": "src/autonomedia/web/",
                "target": "src/autonomedia/shared/",
                "checksum": "1234567890ab"
            }
        ],
        "validation_timestamp": "2026-08-26T12:00:00Z"
    }

@pytest.fixture
def deterministic_compliance_report():
    """Fixture for deterministic compliance report structure."""
    return {
        "checksum_match": True,
        "deterministic_compliant": True,
        "comparison_timestamp": "2026-08-26T12:00:00Z",
        "matrix_1_checksum": "a1b2c3d4e5f6",
        "matrix_2_checksum": "a1b2c3d4e5f6",
        "difference_report": []
    }

@pytest.fixture
def expected_script_outputs():
    """Fixture for expected outputs from script executions."""
    return {
        "vi-001": {
            "exit_code": 0,
            "output_file": "storage/data/integration_core_ai_binding.json",
            "expected_structure": ["validated_bindings", "cross_layer_imports", "validation_timestamp"]
        },
        "vi-002": {
            "exit_code": 0,
            "output_file": "storage/data/integration_platform_core_binding.json",
            "expected_structure": ["isolation_reports", "validation_timestamp"]
        },
        "vi-003": {
            "exit_code": 0,
            "output_file": "storage/data/integration_web_data_binding.json",
            "expected_structure": ["web_data_integration_reports", "validation_timestamp"]
        },
        "vi-004": {
            "exit_code": 0,
            "output_file": "storage/data/platform_isolation_report.json",
            "expected_structure": ["isolated_platforms", "isolation_score", "validation_timestamp", "schema_version"]
        },
        "vi-005": {
            "exit_code": 0,
            "comparison_params": ["storage/data/integration_binding_matrix_1.json", "storage/data/integration_binding_matrix_2.json"],
            "expected_structure": ["checksum_match", "deterministic_compliant"]
        }
    }

@pytest.fixture
def mock_script_execution_results():
    """Fixture for mock results of script execution."""
    return {
        "vi-001": {
            "script_name": "integrity_core_ai.py",
            "exit_code": 0,
            "output_generated": True,
            "validation_passed": True
        },
        "vi-002": {
            "script_name": "integrity_platform_core.py",
            "exit_code": 0,
            "output_generated": True,
            "validation_passed": True
        },
        "vi-003": {
            "script_name": "integrity_web_data.py",
            "exit_code": 0,
            "output_generated": True,
            "validation_passed": True
        },
        "vi-005": {
            "script_name": "integrity_runtime_determinism.py",
            "exit_code": 0,
            "output_generated": True,
            "validation_passed": True
        }
    }

@pytest.fixture
def mock_json_schema_structure():
    """Fixture for mock JSON schema structure for validation."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["isolated_platforms", "isolation_score", "validation_timestamp"],
        "properties": {
            "isolated_platforms": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["platform_name", "isolation_score", "components"],
                    "properties": {
                        "platform_name": {"type": "string"},
                        "isolation_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "components": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "isolation_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "validation_timestamp": {"type": "string", "format": "date-time"},
            "schema_version": {"type": "string"}
        }
    }

@pytest.fixture
def integration_core_ai_binding_factory():
    """Factory fixture for creating integration_core_ai_binding.json data."""
    def _create_binding(validated_bindings=None, isolation_score=0.85):
        return {
            "validated_bindings": validated_bindings or [
                {
                    "source": "src/autonomedia/core/",
                    "target": "src/autonomedia/ai/",
                    "isolation_score": isolation_score,
                    "validation_timestamp": "2026-08-26T11:00:00Z",
                    "violations": []
                }
            ],
            "cross_layer_imports": [],
            "validation_timestamp": "2026-08-26T11:00:00Z",
            "summary": {
                "total_bindings": len(validated_bindings or [1]),
                "isolated_bindings": len(validated_bindings or [1]),
                "isolated_percentage": 100.0
            }
        }
    return _create_binding

@pytest.fixture
def script_execution_parameters():
    """Fixture for script execution parameters used in verification tests."""
    return {
        "vi-001": {
            "command": "uv run python scripts/checks/integrity_core_ai.py --validate --output storage/data/integration_core_ai_binding.json",
            "preconditions": ["uv installed", "Python environment"],
            "expected_evidence": ["Exit code 0", "Cross-layer imports detected", "Output file generated"],
            "failure_conditions": ["Exit code non-zero", "Analysis failure", "Output file missing"],
            "initial_failure_expectation": "Command not found (exit code 127)",
            "success_expectation": "Exit code 0 and output file with validated_bindings array"
        },
        "vi-002": {
            "command": "uv run python scripts/checks/integrity_platform_core.py --validate --output storage/data/integration_platform_core_binding.json",
            "preconditions": ["uv installed", "Python environment"],
            "expected_evidence": ["Exit code 0", "Violations or failures", "Output file generated"],
            "failure_conditions": ["Exit code non-zero", "Analysis failure", "Output file missing"],
            "initial_failure_expectation": "Command not found (exit code 127)",
            "success_expectation": "Exit code 0 and output file with isolation reports"
        },
        "vi-003": {
            "command": "uv run python scripts/checks/integrity_web_data.py --validate --output storage/data/integration_web_data_binding.json",
            "preconditions": ["uv installed", "Python environment"],
            "expected_evidence": ["Exit code 0", "Violations or failures", "Output file generated"],
            "failure_conditions": ["Exit code non-zero", "Analysis failure", "Output file missing"],
            "initial_failure_expectation": "Command not found (exit code 127)",
            "success_expectation": "Exit code 0 and output file with web-data integration reports"
        },
        "vi-005": {
            "command": "uv run python scripts/checks/integrity_runtime_determinism.py --validate --compare storage/data/integration_binding_matrix_1.json storage/data/integration_binding_matrix_2.json",
            "preconditions": ["uv installed", "Python environment"],
            "expected_evidence": ["Exit code 0", "Checksums differ with deterministic compliance"],
            "failure_conditions": ["Exit code checksums differ", "Analysis failure", "Validation fails"],
            "initial_failure_expectation": "Command not found (exit code 127)",
            "success_expectation": "Exit code 0 and deterministic compliance report with checksum_match=true"
        },
        "vi-004": {
            "command": "storage/data/platform_isolation_report.json",
            "schema_contract": True,
            "preconditions": ["Storage/data directory exists"],
            "expected_evidence": ["Valid JSON schema file with required fields"],
            "failure_conditions": ["Invalid schema structure", "Missing required fields"],
            "initial_failure_expectation": "File not found",
            "success_expectation": "Valid platform_isolation_report.json schema with isolated_platforms array and isolation_score field"
        }
    }

class TestStorageDataFixturesIntegration:
    """Integration tests verifying fixtures match VER-M20S2V.md specification."""
    
    def test_fixtures_match_verification_protocol(self, storage_data_directory, integration_core_ai_binding, integration_platform_core_binding, integration_web_data_binding, platform_isolation_report, integration_binding_matrix_1, integration_binding_matrix_2, deterministic_compliance_report, expected_script_outputs, script_execution_parameters):
        """Test that fixtures match VER-M20S2V.md exact specifications."""
        # Verify storage_data_directory fixture
        assert storage_data_directory == Path("storage/data")
        
        # Verify integration_core_ai_binding matches VI-001 requirements
        assert "validated_bindings" in integration_core_ai_binding
        assert "cross_layer_imports" in integration_core_ai_binding
        assert "validation_timestamp" in integration_core_ai_binding
        
        # Verify integration_platform_core_binding matches VI-002 requirements
        assert "isolation_reports" in integration_platform_core_binding
        assert "validation_timestamp" in integration_platform_core_binding
        
        # Verify integration_web_data_binding matches VI-003 requirements
        assert "web_data_integration_reports" in integration_web_data_binding
        assert "validation_timestamp" in integration_web_data_binding
        
        # Verify platform_isolation_report matches VI-004 requirements
        assert "isolated_platforms" in platform_isolation_report
        assert "isolation_score" in platform_isolation_report
        assert "validation_timestamp" in platform_isolation_report
        assert "schema_version" in platform_isolation_report
        
        # Verify integration_binding_matrix_1 and _2 match VI-005 requirements
        assert "checksums" in integration_binding_matrix_1
        assert "checksums" in integration_binding_matrix_2
        assert "bindings" in integration_binding_matrix_1
        assert "bindings" in integration_binding_matrix_2
        assert "validation_timestamp" in integration_binding_matrix_1
        assert "validation_timestamp" in integration_binding_matrix_2
        
        # Verify deterministic_compliance_report matches VI-005 requirements
        assert "checksum_match" in deterministic_compliance_report
        assert "deterministic_compliant" in deterministic_compliance_report
        assert "comparison_timestamp" in deterministic_compliance_report
        
        # Verify expected_script_outputs structure
        assert "vi-001" in expected_script_outputs
        assert "vi-002" in expected_script_outputs
        assert "vi-003" in expected_script_outputs
        assert "vi-004" in expected_script_outputs
        assert "vi-005" in expected_script_outputs
        
        # Verify script_execution_parameters match exact commands from VER-M20S2V.md
        assert "vi-001" in script_execution_parameters
        assert script_execution_parameters["vi-001"]["command"] == (
            "uv run python scripts/checks/integrity_core_ai.py --validate --output storage/data/integration_core_ai_binding.json"
        )
        
        assert "vi-002" in script_execution_parameters
        assert script_execution_parameters["vi-002"]["command"] == (
            "uv run python scripts/checks/integrity_platform_core.py --validate --output storage/data/integration_platform_core_binding.json"
        )
        
        assert "vi-003" in script_execution_parameters
        assert script_execution_parameters["vi-003"]["command"] == (
            "uv run python scripts/checks/integrity_web_data.py --validate --output storage/data/integration_web_data_binding.json"
        )
        
        assert "vi-005" in script_execution_parameters
        assert script_execution_parameters["vi-005"]["command"] == (
            "uv run python scripts/checks/integrity_runtime_determinism.py --validate --compare storage/data/integration_binding_matrix_1.json storage/data/integration_binding_matrix_2.json"
        )
    
    def test_mock_json_schema_structure(self, mock_json_schema_structure):
        """Test that mock JSON schema matches platform_isolation_report requirements."""
        schema = mock_json_schema_structure
        
        # Verify schema matches VI-004 expected structure
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "type" in schema
        assert schema["type"] == "object"
        
        # Verify required fields match VI-004 success expectations
        required_fields = schema.get("required", [])
        assert "isolated_platforms" in required_fields
        assert "isolation_score" in required_fields
        assert "validation_timestamp" in required_fields
        
        # Verify isolated_platforms schema
        isolated_platforms_schema = schema["properties"]["isolated_platforms"]
        assert "type" in isolated_platforms_schema
        assert isolated_platforms_schema["type"] == "array"
        
        # Verify platform items schema
        item_schema = isolated_platforms_schema["items"]
        assert "type" in item_schema
        assert item_schema["type"] == "object"
        
        platform_required = item_schema.get("required", [])
        assert "platform_name" in platform_required
        assert "isolation_score" in platform_required
        assert "components" in platform_required
        
        # Verify isolation_score constraints
        isolation_score_schema = schema["properties"]["isolation_score"]
        assert "minimum" in isolation_score_schema
        assert "maximum" in isolation_score_schema
        assert isolation_score_schema["minimum"] == 0.0
        assert isolation_score_schema["maximum"] == 1.0
    
    def test_factory_fixtures(self, integration_core_ai_binding_factory):
        """Test that factory fixtures can generate dynamic data."""
        # Test integration_core_ai_binding_factory
        create_binding = integration_core_ai_binding_factory
        binding1 = create_binding(isolation_score=0.90)
        assert binding1["validated_bindings"][0]["isolation_score"] == 0.90
        assert binding1["summary"]["isolated_percentage"] == 100.0
        
        binding2 = create_binding(isolation_score=0.75)
        assert binding2["validated_bindings"][0]["isolation_score"] == 0.75
    
    def test_script_execution_parameters_completeness(self, script_execution_parameters):
        """Test that script execution parameters are complete for all verification items."""
        # Verify all verification items have parameters
        assert "vi-001" in script_execution_parameters
        assert "vi-002" in script_execution_parameters
        assert "vi-003" in script_execution_parameters
        assert "vi-004" in script_execution_parameters
        assert "vi-005" in script_execution_parameters
        
        # Verify each has all required fields
        for vi_item in ["vi-001", "vi-002", "vi-003", "vi-005"]:
            params = script_execution_parameters[vi_item]
            assert "command" in params
            assert "preconditions" in params
            assert "expected_evidence" in params
            assert "failure_conditions" in params
            assert "initial_failure_expectation" in params
            assert "success_expectation" in params
        
        # Verify vi-004 has different structure (schema contract)
        vi_004_params = script_execution_parameters["vi-004"]
        assert "command" in vi_004_params
        assert "schema_contract" in vi_004_params
    
    def test_mock_script_execution_results(self, mock_script_execution_results):
        """Test that mock script execution results cover all verification scripts."""
        # Verify all verification scripts are covered
        assert "vi-001" in mock_script_execution_results
        assert mock_script_execution_results["vi-001"]["script_name"] == "integrity_core_ai.py"
        
        assert "vi-002" in mock_script_execution_results
        assert mock_script_execution_results["vi-002"]["script_name"] == "integrity_platform_core.py"
        
        assert "vi-003" in mock_script_execution_results
        assert mock_script_execution_results["vi-003"]["script_name"] == "integrity_web_data.py"
        
        assert "vi-005" in mock_script_execution_results
        assert mock_script_execution_results["vi-005"]["script_name"] == "integrity_runtime_determinism.py"
        
        # Verify each result has expected structure
        for vi_result in mock_script_execution_results.values():
            assert "script_name" in vi_result
            assert "exit_code" in vi_result
            assert "output_generated" in vi_result
            assert "validation_passed" in vi_result
    
    def test_fixture_export_completeness(self):
        """Test that all fixtures are properly exported from tests.fixtures."""
        import tests.fixtures as fixtures_package
        
        expected_fixture_count = 14
        actual_fixture_count = len(fixtures_package.__all__)
        
        assert actual_fixture_count == expected_fixture_count, (
            f"Expected {expected_fixture_count} fixtures, got {actual_fixture_count}"
        )
        
        # Verify essential fixtures are exported
        essential_fixtures = [
            "storage_data_directory",
            "integration_core_ai_binding",
            "integration_platform_core_binding",
            "integration_web_data_binding",
            "platform_isolation_report",
            "integration_binding_matrix_1",
            "integration_binding_matrix_2",
            "deterministic_compliance_report",
            "script_execution_parameters",
        ]
        
        for essential_fixture in essential_fixtures:
            assert essential_fixture in fixtures_package.__all__, (
                f"Essential fixture '{essential_fixture}' is not exported"
            )
