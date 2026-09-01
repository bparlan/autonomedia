import sys
import os

# Simple test of the validation workflow functionality
print("Testing FR-VALIDATION_WORKFLOW Implementation")
print("=" * 60)

# Check if files exist
files_to_check = [
    'scripts/checks/validation_workflow.py',
    'scripts/checks/success_criteria_protocol.py',
    'scripts/checks/compliance_reporting.py',
    'scripts/checks/audit_trail_integration.py',
    'scripts/checks/report_generator.py'
]

print("\n1. Checking file existence:")
for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✓ {file_path}")
    else:
        print(f"✗ {file_path} - MISSING")

# Check the validation_workflow.py content
print("\n2. Checking validation_workflow.py structure:")
if os.path.exists('scripts/checks/validation_workflow.py'):
    with open('scripts/checks/validation_workflow.py', 'r') as f:
        content = f.read()
    
    # Check for key components
    checks = [
        ('class WorkflowExecutionError', 'WorkflowExecutionError class'),
        ('def execute_validation_workflow()', 'execute_validation_workflow function'),
        ('def manage_workflow_state()', 'manage_workflow_state function'),
        ('def write_workflow_state()', 'write_workflow_state function'),
        ('WORKFLOW_STAGES:', 'WORKFLOW_STAGES constant'),
        ('main()', 'main() function'),
        ('import argparse', 'argparse import'),
        ('exit(0)', 'exit(0) for success'),
        ('exit(2)', 'exit(2) for validation failure'),
        ('exit(3)', 'exit(3) for state corruption')
    ]
    
    for check, description in checks:
        if check in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - MISSING")
    
    # Check for key imports
    print("\n3. Checking imports in validation_workflow.py:")
    expected_imports = [
        'from scripts.checks.audit_trail_integration import integrate_audit_trails',
        'from scripts.checks.compliance_reporting import generate_automated_report',
        'from scripts.checks.report_generator import generate_verification_reports',
        'from scripts.checks.success_criteria_protocol import verify_m20_criteria'
    ]
    
    for imp in expected_imports:
        if imp in content:
            print(f"✓ {imp}")
        else:
            print(f"✗ Missing: {imp}")
else:
    print("✗ validation_workflow.py not found")

# Check __init__.py
print("\n4. Checking scripts/checks/__init__.py:")
if os.path.exists('scripts/checks/__init__.py'):
    with open('scripts/checks/__init__.py', 'r') as f:
        init_content = f.read()
    
    # Check for M20S3 modules
    m20s3_modules = [
        'success_criteria_protocol',
        'compliance_reporting', 
        'audit_trail_integration',
        'report_generator',
        'validation_workflow'
    ]
    
    for module in m20s3_modules:
        if f'from .{module} import' in init_content or f'from . {module} import' in init_content.replace(' ', ''):
            print(f"✓ {module} exported in __init__.py")
        else:
            print(f"✗ {module} not found in __init__.py")
else:
    print("✗ __init__.py not found")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
