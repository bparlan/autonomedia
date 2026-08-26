"""Validation workflow module for deterministic validation protocol.

This module implements the FR-VALIDATION_WORKFLOW requirement for deterministic
validation workflow orchestration that manages validation sequence, ensures
idempotency, and maintains validation state across all M20 verification components.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from scripts.checks.audit_trail_integration import integrate_audit_trails
from scripts.checks.compliance_reporting import generate_automated_report
from scripts.checks.report_generator import generate_verification_reports
from scripts.checks.success_criteria_protocol import verify_m20_criteria


class WorkflowExecutionError(Exception):
    """Raised when validation workflow execution fails."""

    def __init__(self, message: str, error_code: int = 3):
        super().__init__(message)
        self.error_code = error_code


WORKFLOW_STAGES: List[str] = [
    'validate_success_criteria',
    'generate_compliance_report',
    'integrate_audit_trails',
    'generate_verification_reports'
]


def write_workflow_state(state: Dict[str, Any], path: str) -> None:
    """Write workflow state to file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w') as f:
            json.dump(state, f, indent=2)

    except Exception as e:
        raise WorkflowExecutionError(f"Failed to write workflow state to {path}: {e}")


def manage_workflow_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Manage workflow execution state."""
    try:
        # Validate required fields
        required_fields = {
            'workflow_id': str,
            'executed_steps': list,
            'step_results': dict,
            'workflow_status': str
        }

        for field, expected_type in required_fields.items():
            if field not in state:
                raise WorkflowExecutionError(f"Missing required field: {field}")
            if not isinstance(state[field], expected_type):
                raise WorkflowExecutionError(
                    f"Invalid type for field {field}: expected {expected_type}, got {type(state[field])}"
                )

        # Validate workflow status
        valid_statuses = ['completed', 'failed', 'corrupted']
        if state['workflow_status'] not in valid_statuses:
            raise WorkflowExecutionError(f"Invalid workflow status: {state['workflow_status']}")

        # Add integrity timestamp if not present
        if 'integrity_timestamp' not in state:
            state['integrity_timestamp'] = datetime.now().isoformat()

        return state

    except Exception as e:
        raise WorkflowExecutionError(f"Failed to manage workflow state: {e}")


def execute_validation_workflow() -> Dict[str, Any]:
    """Execute deterministic validation workflow.

    Returns:
        Dict[str, Any]: Workflow execution results
    """
    workflow_id = f"validation_workflow_{datetime.now().isoformat()}"
    executed_steps: List[str] = []
    step_results: Dict[str, Any] = {}

    try:
        executed_steps.append('validate_success_criteria')
        success_criteria_results = verify_m20_criteria()
        step_results['validate_success_criteria'] = {
            'status': 'completed',
            'result': success_criteria_results,
            'timestamp': datetime.now().isoformat()
        }

        executed_steps.append('generate_compliance_report')
        compliance_report = generate_automated_report(success_criteria_results)
        step_results['generate_compliance_report'] = {
            'status': 'completed',
            'result': compliance_report,
            'timestamp': datetime.now().isoformat()
        }

        executed_steps.append('integrate_audit_trails')
        audit_trail_results = integrate_audit_trails(
            ['storage/data/success_criteria_report.json',
             'storage/data/automated_compliance_report.json']
        )
        step_results['integrate_audit_trails'] = {
            'status': 'completed',
            'result': audit_trail_results,
            'timestamp': datetime.now().isoformat()
        }

        executed_steps.append('generate_verification_reports')
        report_results = generate_verification_reports({
            'success_criteria': success_criteria_results,
            'compliance': compliance_report,
            'audit_trail': audit_trail_results
        })
        step_results['generate_verification_reports'] = {
            'status': 'completed',
            'result': report_results,
            'timestamp': datetime.now().isoformat()
        }

        workflow_status = 'completed'

    except Exception as e:
        workflow_status = 'failed'
        step_results['error'] = {
            'status': 'failed',
            'error_message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        raise WorkflowExecutionError(f"Validation workflow failed: {e}")

    return {
        'workflow_id': workflow_id,
        'executed_steps': executed_steps,
        'step_results': step_results,
        'workflow_status': workflow_status
    }


def main() -> None:
    """Main entry point for validation workflow CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Execute deterministic validation workflow'
    )
    parser.add_argument('--execute', action='store_true', help='Execute validation workflow')
    parser.add_argument('--mode', choices=['full', 'quick', 'deep'], 
                       default='full', help='Validation workflow mode')
    parser.add_argument('--output', required=True, help='Output file path for workflow state')

    args = parser.parse_args()

    if not args.execute:
        parser.error("The --execute flag is required")

    try:
        results = execute_validation_workflow()
        managed_state = manage_workflow_state(results)
        write_workflow_state(managed_state, args.output)
        exit(0)

    except WorkflowExecutionError as e:
        print(f"Validation workflow error: {e}", file=sys.stderr)
        exit(2)

    except Exception as e:
        print(f"Workflow corruption error: {e}", file=sys.stderr)
        exit(3)


if __name__ == '__main__':
    main()