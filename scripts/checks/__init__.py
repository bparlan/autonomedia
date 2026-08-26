"""Integration binding validation package."""

# Import all modules to make them available
import importlib

# Dynamically import all modules
for module_name in [
    'integrity_core_ai',
    'integrity_platform_core', 
    'integrity_web_data',
    'integrity_platform_isolation',
    'integrity_runtime_determinism',
    'success_criteria_protocol',
    'compliance_reporting',
    'audit_trail_integration',
    'report_generator',
    'validation_workflow'
]:
    try:
        module = importlib.import_module(f'.{module_name}', __name__)
        globals()[module_name] = module
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")

# Create a simple __all__ list with all expected functions from FR-VALIDATION_WORKFLOW
__all__ = [
    # FR-VALIDATION_WORKFLOW functions
    'verify_m20_criteria',
    'generate_automated_report',
    'generate_verification_reports',
    'integrate_audit_trails',
    'execute_validation_workflow',
    'manage_workflow_state',
    'write_workflow_state',
    'WorkflowExecutionError',
    'WORKFLOW_STAGES',
    'SuccessCriteriaViolation',
    'SUCCESS_CRITERIA_MAP',
    'ComplianceReportError',
    'COMPLIANCE_REPORT_TEMPLATES',
    'AuditTrailError',
    'AUDIT_TRAIL_SCHEMA',
    'ReportGenerationError',
    'REPORT_FORMATS',
    
    # Other functions from original modules
    'validate_core_ai_integrity',
    'analyze_integration_bindings',
    'write_integration_report',
    'validate_platform_core_integrity',
    'check_isolation_violations',
    'generate_isolation_report',
    'analyze_web_data_integration',
    'validate_output_schema',
    'write_report',
    'analyze_platform_isolation',
    'get_file_checksum',
    'run_integration_validation',
    'generate_binding_matrix',
    'compare_matrices'
]