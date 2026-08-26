"""
Test fixtures for storage/data directory structure validation.

This module provides test fixtures that simulate the storage/data directory
contents required by the M20S2 verification protocol (VI-001 through VI-005).

The fixtures support testing:
- Core AI integration binding validation (VI-001)
- Platform core integration validation (VI-002)
- Web data integration validation (VI-003)
- Platform isolation schema validation (VI-004)
- Runtime determinism validation (VI-005)
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List

# Test fixture data that matches the expected structure from VER-M20S2V.md

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

# Factory fixtures for creating test-specific data

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
def integration_binding_matrix_factory():
    """Factory fixture for creating integration_binding_matrix.json data."""
    def _create_matrix(checksums=None, bindings=None):
        return {
            "checksums": checksums or {
                "core": "a1b2c3d4e5f6",
                "platform": "f6e5d4c3b2a1",
                "web": "1234567890ab",
                "ai": "cdef123456"
            },
            "bindings": bindings or [
                {
                    "source": "src/autonomedia/core/",
                    "target": "src/autonomedia/ai/",
                    "checksum": "a1b2c3d4e5f6"
                }
            ],
            "validation_timestamp": "2026-08-26T11:00:00Z"
        }
    return _create_matrix

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
        }
    }