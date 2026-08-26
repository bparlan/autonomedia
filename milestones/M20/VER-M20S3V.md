---
id: VER-M20S3V
type: verification
title: "Success Criteria Verification Protocol Implementation and Automated Compliance Reporting Verification Protocol"
milestone_id: M20
status: draft
derived_from:
  - M20
  - SPEC-M20S3

---

# Verification Protocol: Success Criteria Verification Protocol Implementation and Automated Compliance Reporting

## Verification Items

### FR-SUCCESS_CRITERIA_PROTOCOL (VI-001 to VI-005)

#### VI-001
- **Verification ID**: VI-001
- **Source Requirement ID**: FR-SUCCESS_CRITERIA_PROTOCOL
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/success_criteria_protocol.py --verify --output storage/data/success_criteria_report.json
- **Preconditions**: System has `uv` installed and Python environment, all prerequisite M20 verification scripts available in scripts/checks/
- **Input or Fixture**: --verify flag executed with output path specified
- **Expected Evidence**: Exit code 0 when all M20 success criteria verified; storage/data/success_criteria_report.json created with verified_criteria, failed_criteria, overall_success, and compliance_score fields
- **Failure Condition**: Exit code 2 when criteria failures detected; exit code 3 when verification fails; output file not generated or missing required fields
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 with success_criteria_report.json containing verified_criteria array, failed_criteria array, overall_success boolean true, compliance_score float >= 1.0

#### VI-002
- **Verification ID**: VI-002
- **Source Requirement ID**: FR-SUCCESS_CRITERIA_PROTOCOL
- **Verification Method**: SCHEMA_CONTRACT
- **Target**: storage/data/success_criteria_report.json schema validation with required fields: verified_criteria, failed_criteria, overall_success, compliance_score
- **Preconditions**: success_criteria_report.json exists in storage/data/
- **Input or Fixture**: JSON schema validation of success criteria report
- **Expected Evidence**: Valid JSON schema structure with all required fields present and correct types
- **Failure Condition**: Invalid schema structure or missing required fields
- **Initial Failure Expectation**: File not found (exit code 127)
- **Post-Implementation Success Expectation**: Valid success_criteria_report.json schema with verified_criteria array of strings, failed_criteria array of strings, overall_success boolean true, compliance_score float between 0.0 and 1.0

#### VI-003
- **Verification ID**: VI-003
- **Source Requirement ID**: FR-SUCCESS_CRITERIA_PROTOCOL
- **Verification Method**: DETERMINISM_TEST
- **Target**: Multiple executions of success_criteria_protocol.py to verify deterministic behavior
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Same input conditions across multiple runs
- **Expected Evidence**: Identical success_criteria_report.json files across multiple executions
- **Failure Condition**: Different output files across runs or non-deterministic execution
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Deterministic execution producing identical success_criteria_report.json across multiple runs

#### VI-004
- **Verification ID**: VI-004
- **Source Requirement ID**: FR-SUCCESS_CRITERIA_PROTOCOL
- **Verification Method**: COMPONENT_INTEGRATION
- **Target**: Integration with M20S1 and M20S2 verification components
- **Preconditions**: storage/data/success_criteria_report.json exists
- **Input or Fixture**: Generated success criteria report contains all layer verification results
- **Expected Evidence**: Complete cross-layer integration with deterministic results across all M20 components
- **Failure Condition**: Missing layer data, inconsistent integration results
- **Initial Failure Expectation**: Integration not implemented
- **Post-Implementation Success Expectation**: Complete cross-layer integration with deterministic results across all M20 components

#### VI-005
- **Verification ID**: VI-005
- **Source Requirement ID**: FR-SUCCESS_CRITERIA_PROTOCOL
- **Verification Method**: ERROR_BOUNDARY_TEST
- **Target**: Error conditions in success criteria protocol execution
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Error injection scenarios (invalid inputs, missing dependencies)
- **Expected Evidence**: Proper error handling with appropriate exit codes (2 for criteria failures, 3 for verification failures)
- **Failure Condition**: Improper error handling or incorrect exit codes
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Proper error handling with correct exit codes and meaningful error messages

### FR-AUTOMATED_COMPLIANCE_REPORTING (VI-006 to VI-010)

#### VI-006
- **Verification ID**: VI-006
- **Source Requirement ID**: FR-AUTOMATED_COMPLIANCE_REPORTING
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/compliance_reporting.py --generate --input storage/data/success_criteria_report.json --output storage/data/automated_compliance_report.json
- **Preconditions**: System has `uv` installed and Python environment, success_criteria_report.json exists in storage/data/
- **Input or Fixture**: --generate flag with input and output paths specified
- **Expected Evidence**: Exit code 0 if report generated; storage/data/automated_compliance_report.json created with report_metadata, layer_verification_results, overall_compliance_assessment, and audit_trail_reference fields
- **Failure Condition**: Exit code 3 if report generation fails; output file not generated or invalid schema structure
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 with automated_compliance_report.json containing valid report_metadata, layer_verification_results array, overall_compliance_assessment with compliance_score >= 1.0, audit_trail_reference array

#### VI-007
- **Verification ID**: VI-007
- **Source Requirement ID**: FR-AUTOMATED_COMPLIANCE_REPORTING
- **Verification Method**: SCHEMA_CONTRACT
- **Target**: storage/data/automated_compliance_report.json schema validation with required fields: report_metadata, layer_verification_results, overall_compliance_assessment, audit_trail_reference
- **Preconditions**: automated_compliance_report.json exists in storage/data/
- **Input or Fixture**: JSON schema validation of automated compliance report
- **Expected Evidence**: Valid JSON schema structure with all required fields present and correct types
- **Failure Condition**: Invalid schema structure or missing required fields
- **Initial Failure Expectation**: File not found (exit code 127)
- **Post-Implementation Success Expectation**: Valid automated_compliance_report.json schema with report_metadata object containing timestamp, layer_verification_results array with layer_name and compliance_score, overall_compliance_assessment with overall_score float, audit_trail_reference array with references

#### VI-008
- **Verification ID**: VI-008
- **Source Requirement ID**: FR-AUTOMATED_COMPLIANCE_REPORTING
- **Verification Method**: INTEGRITY_VALIDATION
- **Target**: Audit trail integration with compliance reporting
- **Preconditions**: verification_audit_trail.jsonl exists in storage/data/
- **Input or Fixture**: Audit trail entries with integrity_hash fields
- **Expected Evidence**: All audit trail entries have valid SHA-256 integrity hashes matching content
- **Failure Condition**: Invalid integrity hashes or corrupted audit trail entries
- **Initial Failure Expectation**: Audit trail integrity validation not implemented
- **Post-Implementation Success Expectation**: All audit trail entries pass integrity validation with valid SHA-256 hashes

#### VI-009
- **Verification ID**: VI-009
- **Source Requirement ID**: FR-AUTOMATED_COMPLIANCE_REPORTING
- **Verification Method**: COMPONENT_INTEGRATION
- **Target**: Integration with M20S1 and M20S2 verification components
- **Preconditions**: storage/data/success_criteria_report.json and storage/data/verification_audit_trail.jsonl exist
- **Input or Fixture**: Generated compliance report contains all layer_verification_results and deterministic overall_compliance_assessment
- **Expected Evidence**: Complete cross-layer integration with deterministic results across all M20 components
- **Failure Condition**: Missing layer data, inconsistent integration results
- **Initial Failure Expectation**: Integration not implemented
- **Post-Implementation Success Expectation**: Complete cross-layer integration with deterministic results across all M20 components

#### VI-010
- **Verification ID**: VI-010
- **Source Requirement ID**: FR-AUTOMATED_COMPLIANCE_REPORTING
- **Verification Method**: DETERMINISTIC_VALIDATION
- **Target**: Deterministic compliance reporting validation
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Same input conditions across multiple runs
- **Expected Evidence**: Identical automated_compliance_report.json files across multiple executions
- **Failure Condition**: Different output files across runs or non-deterministic execution
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Deterministic execution producing identical automated_compliance_report.json across multiple runs

### FR-AUDIT_TRAIL_INTEGRATION (VI-011 to VI-015)

#### VI-011
- **Verification ID**: VI-011
- **Source Requirement ID**: FR-AUDIT_TRAIL_INTEGRATION
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/audit_trail_integration.py --integrate --source storage/data/ --output storage/data/verification_audit_trail.jsonl
- **Preconditions**: System has `uv` installed and Python environment, verification audit trails exist in storage/data/
- **Input or Fixture**: --integrate flag with source and output paths specified
- **Expected Evidence**: Exit code 0 when audit trail integrated; storage/data/verification_audit_trail.jsonl created with verification_session_id, component_verification, timestamp, verification_result, and integrity_hash fields
- **Failure Condition**: Exit code 2 when integration failures; exit code 3 when log corruption detected; output file not generated or invalid entry schema
- **Initial Failure Expectation**: Command not found (exit code 127)
- **Post-Implementation Success Expectation**: Exit code 0 with verification_audit_trail.jsonl containing entries with verification_session_id, component_verification array, timestamp ISO string, verification_result "success", integrity_hash SHA-256 string

#### VI-012
- **Verification ID**: VI-012
- **Source Requirement ID**: FR-AUDIT_TRAIL_INTEGRATION
- **Verification Method**: SCHEMA_CONTRACT
- **Target**: storage/data/verification_audit_trail.jsonl schema validation with required fields: verification_session_id, component_verification, timestamp, verification_result, integrity_hash
- **Preconditions**: verification_audit_trail.jsonl exists in storage/data/
- **Input or Fixture**: JSON schema validation of each audit trail entry
- **Expected Evidence**: Valid JSON lines format with all required fields present and correct types for each entry
- **Failure Condition**: Invalid schema structure or missing required fields in any entry
- **Initial Failure Expectation**: File not found (exit code 127)
- **Post-Implementation Success Expectation**: Valid verification_audit_trail.jsonl with entries containing verification_session_id UUID, component_verification array, timestamp ISO string, verification_result "success" or "failure", integrity_hash SHA-256 string

#### VI-013
- **Verification ID**: VI-013
- **Source Requirement ID**: FR-AUDIT_TRAIL_INTEGRATION
- **Verification Method**: INTEGRITY_VALIDATION
- **Target**: Audit trail integrity validation with cryptographic hash verification
- **Preconditions**: verification_audit_trail.jsonl exists in storage/data/
- **Input or Fixture**: Audit trail entries with integrity_hash fields
- **Expected Evidence**: All audit trail entries have valid SHA-256 integrity hashes matching content
- **Failure Condition**: Invalid integrity hashes or corrupted audit trail entries
- **Initial Failure Expectation**: Audit trail integrity validation not implemented
- **Post-Implementation Success Expectation**: All audit trail entries pass integrity validation with valid SHA-256 hashes

#### VI-014
- **Verification ID**: VI-014
- **Source Requirement ID**: FR-AUDIT_TRAIL_INTEGRATION
- **Verification Method**: DETERMINISM_TEST
- **Target**: Multiple executions of audit_trail_integration.py to verify deterministic behavior
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Same input conditions across multiple runs
- **Expected Evidence**: Identical verification_audit_trail.jsonl files across multiple executions
- **Failure Condition**: Different output files across runs or non-deterministic execution
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Deterministic execution producing identical verification_audit_trail.jsonl across multiple runs

#### VI-015
- **Verification ID**: VI-015
- **Source Requirement ID**: FR-AUDIT_TRAIL_INTEGRATION
- **Verification Method**: COMPONENT_INTEGRATION
- **Target**: Integration audit trail with all M20 verification components
- **Preconditions**: All verification components implemented and accessible
- **Input or Fixture**: Full audit trail integration execution
- **Expected Evidence**: Unified verification audit trail executing all components successfully in defined WORKFLOW_STAGES sequence
- **Failure Condition**: Component integration failures or missing integration points
- **Initial Failure Expectation**: Scripts not implemented
- **Post-Implementation Success Expectation**: Seamless integration with all verification components producing unified compliance results

### FR-REPORT_GENERATION (VI-016 to VI-020)

#### VI-016
- **Verification ID**: VI-016
- **Source Requirement ID**: FR-REPORT_GENERATION
- **Verification Method**: FILESYSTEM_STATE_CONTRACT
- **Target**: scripts/checks/report_generator.py generating storage/data/m20_verification_report.html and storage/data/m20_verification_report.pdf
- **Preconditions**: System has `uv` installed and Python environment, compliance data available from automated_compliance_report.json
- **Input or Fixture**: Report generation with compliance data input
- **Expected Evidence**: Files storage/data/m20_verification_report.html and storage/data/m20_verification_report.pdf exist and are non-empty; report generation successful
- **Failure Condition**: Files not generated or empty; exit code 3 if report generation fails
- **Initial Failure Expectation**: Script not found (exit code 127)
- **Post-Implementation Success Expectation**: Both storage/data/m20_verification_report.html and storage/data/m20_verification_report.pdf files created with HTML report containing executive summary and PDF report containing detailed verification results

#### VI-017
- **Verification ID**: VI-017
- **Source Requirement ID**: FR-REPORT_GENERATION
- **Verification Method**: SCHEMA_CONTRACT
- **Target**: storage/data/m20_verification_report.html schema validation (HTML structure validation)
- **Preconditions**: m20_verification_report.html exists in storage/data/
- **Input or Fixture**: HTML structure validation (contains executive summary, verification results, audit trails)
- **Expected Evidence**: HTML file contains required sections: executive summary, detailed verification results, audit trails, compliance evidence
- **Failure Condition**: HTML structure invalid or missing required sections
- **Initial Failure Expectation**: File not found (exit code 127)
- **Post-Implementation Success Expectation**: Valid m20_verification_report.html containing executive_summary div, detailed_results section, audit_trails table, compliance_evidence section

#### VI-018
- **Verification ID**: VI-018
- **Source Requirement ID**: FR-REPORT_GENERATION
- **Verification Method**: DETERMINISM_TEST
- **Target**: Multiple executions of report_generator.py to verify deterministic behavior
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Same input conditions across multiple runs
- **Expected Evidence**: Identical m20_verification_report.html and m20_verification_report.pdf files across multiple executions
- **Failure Condition**: Different output files across runs or non-deterministic execution
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Deterministic execution producing identical report files across multiple runs

#### VI-019
- **Verification ID**: VI-019
- **Source Requirement ID**: FR-REPORT_GENERATION
- **Verification Method**: ERROR_BOUNDARY_TEST
- **Target**: Error conditions in report generation execution
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Error injection scenarios (missing dependencies, invalid inputs)
- **Expected Evidence**: Proper error handling with appropriate exit codes (3 for report generation failures)
- **Failure Condition**: Improper error handling or incorrect exit codes
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Proper error handling with correct exit codes and meaningful error messages

#### VI-020
- **Verification ID**: VI-020
- **Source Requirement ID**: FR-REPORT_GENERATION
- **Verification Method**: COMPONENT_INTEGRATION
- **Target**: Integration report generator with all verification components
- **Preconditions**: All verification components implemented and accessible
- **Input or Fixture**: Full report generation execution
- **Expected Evidence**: Unified verification reports executing all components successfully in defined WORKFLOW_STAGES sequence
- **Failure Condition**: Component integration failures or missing integration points
- **Initial Failure Expectation**: Scripts not implemented
- **Post-Implementation Success Expectation**: Seamless integration with all verification components producing unified compliance results

### FR-VALIDATION_WORKFLOW (VI-021 to VI-030)

#### VI-021
- **Verification ID**: VI-021
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: SCRIPT_EXECUTION
- **Target**: uv run python scripts/checks/validation_workflow.py --execute --mode full --output storage/data/validation_workflow_state.json
- **Preconditions**: System has `uv` installed and Python environment, all verification scripts available in scripts/checks/
- **Input or Fixture**: --execute flag with mode full and output path specified
- **Expected Evidence**: Exit code 0 when workflow completed; storage/data/validation_workflow_state.json created with workflow_id, executed_steps, step_results, workflow_status fields
- **Failure Condition**: Exit code 2 when validation fails; exit code 3 when workflow state corruption; output file not generated or invalid state structure
- **Initial Failure Expectation**: Command not found (exit code 127) or script not implemented
- **Post-Implementation Success Expectation**: Exit code 0 with validation_workflow_state.json containing workflow_id UUID, executed_steps array with all steps completed, step_results array with success results, workflow_status "completed"

#### VI-022
- **Verification ID**: VI-022
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: SCHEMA_CONTRACT
- **Target**: storage/data/validation_workflow_state.json schema validation with required fields: workflow_id, executed_steps, step_results, workflow_status
- **Preconditions**: validation_workflow_state.json exists in storage/data/
- **Input or Fixture**: JSON schema validation of validation workflow state
- **Expected Evidence**: Valid JSON schema structure with all required fields present and correct types
- **Failure Condition**: Invalid schema structure or missing required fields
- **Initial Failure Expectation**: File not found (exit code 127)
- **Post-Implementation Success Expectation**: Valid validation_workflow_state.json with workflow_id UUID, executed_steps array with step objects containing step_name and status, step_results array with result objects, workflow_status "completed"

#### VI-023
- **Verification ID**: VI-023
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: DETERMINISM_TEST
- **Target**: Multiple executions of validation_workflow.py to verify deterministic behavior
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Same input conditions across multiple runs
- **Expected Evidence**: Identical validation_workflow_state.json files across multiple executions
- **Failure Condition**: Different output files across runs or non-deterministic execution
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Deterministic execution producing identical validation_workflow_state.json across multiple runs

#### VI-024
- **Verification ID**: VI-024
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: ERROR_BOUNDARY_TEST
- **Target**: Error conditions in validation workflow execution
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Error injection scenarios (missing prerequisites, corrupt state)
- **Expected Evidence**: Proper error handling with appropriate exit codes (2 for validation failures, 3 for state corruption)
- **Failure Condition**: Improper error handling or incorrect exit codes
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Proper error handling with correct exit codes and meaningful error messages

#### VI-025
- **Verification ID**: VI-025
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: STATE_MANAGEMENT
- **Target**: scripts.checks.validation_workflow.manage_workflow_state() function
- **Preconditions**: System has `uv` installed and Python environment
- **Input or Fixture**: Workflow state dictionary from execute_validation_workflow()
- **Expected Evidence**: Validated workflow state with proper error handling for invalid states
- **Failure Condition**: Invalid state management or validation failures not caught
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Robust state management with proper validation and error handling for corrupted states

#### VI-026
- **Verification ID**: VI-026
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: WORKFLOW_STAGES_INTEGRITY
- **Target**: scripts.checks.validation_workflow.WORKFLOW_STAGES constant
- **Preconditions**: validation_workflow.py module exists
- **Input or Fixture**: WORKFLOW_STAGES definition
- **Expected Evidence**: WORKFLOW_STAGES defined as list with ordered stages: validate_success_criteria, generate_compliance_report, integrate_audit_trails, generate_verification_reports
- **Failure Condition**: Missing or incorrectly ordered workflow stages
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: WORKFLOW_STAGES properly defined with correct stage ordering

#### VI-027
- **Verification ID**: VI-027
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: COMPONENT_INTEGRATION
- **Target**: Integration validation workflow with audit trail and compliance reporting
- **Preconditions**: All verification components implemented and accessible
- **Input or Fixture**: Full workflow execution mode
- **Expected Evidence**: Unified verification workflow executing all components successfully in defined WORKFLOW_STAGES sequence
- **Failure Condition**: Component integration failures or missing integration points
- **Initial Failure Expectation**: Scripts not implemented
- **Post-Implementation Success Expectation**: Seamless integration with all verification components producing unified compliance results

#### VI-028
- **Verification ID**: VI-028
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: FINAL_VERIFICATION
- **Target**: Complete M20 validation workflow execution
- **Preconditions**: All prerequisite verification scripts available and functional
- **Input or Fixture**: Complete validation workflow execution
- **Expected Evidence**: Full M20 validation completed with all components verified across all M20 success criteria
- **Failure Condition**: Incomplete validation or component failures
- **Initial Failure Expectation**: Scripts not implemented
- **Post-Implementation Success Expectation**: Complete M20 validation workflow execution with all success criteria verified and comprehensive compliance report generated

#### VI-029
- **Verification ID**: VI-029
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: AUDIT_TRAIL_INTEGRATION
- **Target**: Validation workflow audit trail integration
- **Preconditions**: Audit trail system operational
- **Input or Fixture**: Workflow execution with audit logging
- **Expected Evidence**: Validation workflow entries in unified audit trail with verification_session_id, component_verification, timestamp, verification_result, integrity_hash
- **Failure Condition**: Missing audit trail entries or corrupted integration
- **Initial Failure Expectation**: Scripts not implemented
- **Post-Implementation Success Expectation**: Proper audit trail integration with validation workflow entries and integrity hashes

#### VI-030
- **Verification ID**: VI-030
- **Source Requirement ID**: FR-VALIDATION_WORKFLOW
- **Verification Method**: BACKWARD_COMPATIBILITY
- **Target**: Backward compatibility with existing M20 verification
- **Preconditions**: Existing M20 verification scripts and components
- **Input or Fixture**: Validation workflow with existing component compatibility
- **Expected Evidence**: No breaking changes to existing verification processes
- **Failure Condition**: Breaking changes to existing verification
- **Initial Failure Expectation**: Script not implemented
- **Post-Implementation Success Expectation**: Validation workflow maintains backward compatibility with existing M20 verification components

## Verification Protocol Summary

This verification protocol covers all aspects of the M20S3 specification:

1. **FR-SUCCESS_CRITERIA_PROTOCOL** (VI-001 to VI-005): Success criteria verification and report generation
2. **FR-AUTOMATED_COMPLIANCE_REPORTING** (VI-006 to VI-010): Automated compliance reporting system
3. **FR-AUDIT_TRAIL_INTEGRATION** (VI-011 to VI-015): Unified audit trail integration
4. **FR-REPORT_GENERATION** (VI-016 to VI-020): Human-readable verification report generation
5. **FR-VALIDATION_WORKFLOW** (VI-021 to VI-030): Deterministic validation workflow execution

All verification items reference the specific semantic FR IDs for traceability and ensure each functional requirement is comprehensively tested for observable behavior, deterministic execution, and proper integration with the M20 verification ecosystem.

#### Next Steps

Run `/generate-verification` to create the verification protocol for this specification.