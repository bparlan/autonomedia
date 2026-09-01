import sys
import os
sys.path.insert(0, '.')

# Import all M20S3 modules
from scripts.checks.success_criteria_protocol import verify_m20_criteria
from scripts.checks.validation_workflow import execute_validation_workflow, WorkflowExecutionError

print("✓ M20S3 modules imported successfully")

# Test success criteria verification
print("\n1. Testing success criteria verification...")
try:
    results = verify_m20_criteria()
    print(f"✓ verify_m20_criteria() executed successfully")
    print(f"  - verified_criteria: {results.get('verified_criteria', [])}")
    print(f"  - overall_success: {results.get('overall_success', False)}")
    print(f"  - compliance_score: {results.get('compliance_score', 0.0)}")
except Exception as e:
    print(f"✗ verify_m20_criteria() failed: {e}")
    import traceback
    traceback.print_exc()

# Test validation workflow
print("\n2. Testing validation workflow...")
try:
    workflow_results = execute_validation_workflow()
    print(f"✓ execute_validation_workflow() executed successfully")
    print(f"  - workflow_id: {workflow_results.get('workflow_id', 'N/A')}")
    print(f"  - workflow_status: {workflow_results.get('workflow_status', 'N/A')}")
    print(f"  - executed_steps: {len(workflow_results.get('executed_steps', []))} steps")
except WorkflowExecutionError as e:
    print(f"⚠ Workflow execution error (expected): {e}")
    print(f"  - Error code: {e.error_code}")
except Exception as e:
    print(f"✗ execute_validation_workflow() failed: {e}")
    import traceback
    traceback.print_exc()

# Test CLI interface
print("\n3. Testing CLI interface...")
try:
    import subprocess
    result = subprocess.run(
        ['uv', 'run', 'python', 'scripts/checks/validation_workflow.py', 
         '--execute', '--mode', 'full', '--output', 
         'storage/data/validation_workflow_state.json'],
        capture_output=True,
        text=True,
        cwd='.'
    )
    print(f"✓ CLI execution completed")
    print(f"  - Exit code: {result.returncode}")
    if result.returncode == 0:
        print(f"  ✓ CLI exited successfully (0)")
    elif result.returncode == 2:
        print(f"  ⚠ CLI exited with validation failure (2)")
    elif result.returncode == 3:
        print(f"  ⚠ CLI exited with workflow corruption (3)")
    else:
        print(f"  ✗ CLI exited with unexpected code ({result.returncode})")
        print(f"  - stderr: {result.stderr[:200]}...")
        
except Exception as e:
    print(f"✗ CLI test failed: {e}")

print("\n=== VERIFICATION COMPLETE ===")
