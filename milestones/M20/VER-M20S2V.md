---
id: VER-M20S2V
type: verification
title: "Integration Binding Validation Verification Protocol"
milestone_id: M20
status: draft
derived_from:
  - M20
  - SPEC-M20S2

---

# Verification Protocol: Integration Binding Validation Verification Protocol

## Verification Items

### VI-001
- **Verification ID**: VI-001
- **Source Requirement ID**: FR-INTEGRITY_CORE_AI_BINDING
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/integrity_core_ai.py --validate --output storage/data/integration_core_ai_binding.json
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: --validate flag executed
- **Expected Evidence**: Exit code 0, cross-layer imports detected, or analysis fails and storage/data/integration_core_ai_binding.json`,integration_core_ai_binding.json` created with validated_bindings array
- **Failure Condition**: Exit code cross-layer imports detected or analysis fails or output file not generated
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 and storage/data/integration_core_ai_binding.json`,integration_core_ai_binding.json` created with validated_bindings array

### VI-002
- **Verification ID**: VI-002
- **Source Requirement ID**: FR-INTEGRITY_PLATFORM_CORE_BINDING
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/integrity_platform_core.py --validate --output storage/data/integration_platform_core_binding.json
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: --validate flag executed
- **Expected Evidence**: Exit code 0, violations or failures, or analysis fails and storage/data/integration_platform_core_binding.json`,integration_platform_core_binding.json` created with isolation reports
- **Failure Condition**: Exit code violations or failures or analysis fails or output file not generated
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 and storage/data/integration_platform_core_binding.json`,integration_platform_core_binding.json` created with isolation reports

### VI-003
- **Verification ID**: VI-003
- **Source Requirement ID**: FR-INTEGRITY_WEB_DATA_BINDING
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/integrity_web_data.py --validate --output storage/data/integration_web_data_binding.json
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: --validate flag executed
- **Expected Evidence**: Exit code 0, violations or failures, or analysis fails and storage/data/integration_web_data_binding.json`,integration_web_data_binding.json` created with web-data integration reports
- **Failure Condition**: Exit code violations or failures or analysis fails or output file not generated
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 and storage/data/integration_web_data_binding.json`,integration_web_data_binding.json` created with web-data integration reports

### VI-004
- **Verification ID**: VI-004
- **Source Requirement ID**: FR-INTEGRITY_PLATFORM_ISOLATION
- **Verification Method**: SCHEMA_CONTRACT
- **Target**: storage/data/platform_isolation_report.json with defined schema for platform isolation validation
- **Preconditions**: Storage/data directory exists
- **Input or Fixture**: Platform isolation validation script execution
- **Expected Evidence**: Valid JSON schema file with required fields
- **Failure Condition**: Invalid schema structure or missing required fields
- **Initial Failure Expectation**: File not found (exit code 127)
- **Post-Implementation Success Expectation**: Valid platform_isolation_report.json schema with isolated_platforms array and isolation_score field

### VI-005
- **Verification ID**: VI-005
- **Source Requirement ID**: FR-INTEGRITY_RUNTIME_DETERMINISM
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/integrity_runtime_determinism.py --validate --compare storage/data/integration_binding_matrix_1.json storage/data/integration_binding_matrix_2.json
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: --validate flag executed
- **Expected Evidence**: Exit code 0 or checksums differ with deterministic compliance report generated showing checksum_match=true
- **Failure Condition**: Exit code checksums differ or analysis failure or validation fails
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 and deterministic compliance report generated with checksum_match=true

