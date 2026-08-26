"""
Test fixtures for the autonomedia-snapshot project.

This package provides test fixtures for integration, platform, and runtime validation
tests as part of the M20S2 verification protocol (VI-001 through VI-005).

The fixtures support:
- Core AI integration binding validation (VI-001)
- Platform core integration validation (VI-002)
- Web data integration validation (VI-003)
- Platform isolation schema validation (VI-004)
- Runtime determinism validation (VI-005)

Fixtures are organized by functional domain:
- storage_data_fixtures.py: storage/data directory structure validation
- rewrite/: rewrite-specific test fixtures
"""

from .storage_data_fixtures import (
    # Storage/data directory fixtures
    storage_data_directory,
    integration_core_ai_binding,
    integration_platform_core_binding,
    integration_web_data_binding,
    platform_isolation_report,
    integration_binding_matrix_1,
    integration_binding_matrix_2,
    deterministic_compliance_report,
    expected_script_outputs,
    mock_script_execution_results,
    mock_json_schema_structure,
    integration_core_ai_binding_factory,
    integration_binding_matrix_factory,
    script_execution_parameters,
)

__all__ = [
    # Storage/data directory fixtures
    "storage_data_directory",
    "integration_core_ai_binding",
    "integration_platform_core_binding",
    "integration_web_data_binding",
    "platform_isolation_report",
    "integration_binding_matrix_1",
    "integration_binding_matrix_2",
    "deterministic_compliance_report",
    "expected_script_outputs",
    "mock_script_execution_results",
    "mock_json_schema_structure",
    "integration_core_ai_binding_factory",
    "integration_binding_matrix_factory",
    "script_execution_parameters",
]