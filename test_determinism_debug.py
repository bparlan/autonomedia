import json
import os
import subprocess
import sys

def run_script(script_path, output_file=None, compare_files=None):
    """Run a validation script and return the result."""
    cmd = [sys.executable, script_path]

    if output_file:
        cmd.extend(["--validate", "--output", output_file])

    if compare_files:
        cmd.extend(["--compare"] + compare_files)

    env = os.environ.copy()
    env["REPO_ROOT"] = "."

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return result

# Clean up previous runs
for output_file in ["storage/data/integration_binding_matrix_1.json", "storage/data/integration_binding_matrix_2.json"]:
    if os.path.exists(output_file):
        os.remove(output_file)

# Generate first binding matrix
print("Generating first binding matrix...")
result1 = run_script("scripts/checks/integrity_runtime_determinism.py", output_file="storage/data/integration_binding_matrix_1.json")
print(f"Exit code 1: {result1.returncode}")

# Generate second binding matrix
print("\nGenerating second binding matrix...")
result2 = run_script("scripts/checks/integrity_runtime_determinism.py", output_file="storage/data/integration_binding_matrix_2.json")
print(f"Exit code 2: {result2.returncode}")

# Now compare them using the script's built-in --compare option
print("\nComparing matrices using script's --compare option...")
compare_result = run_script("scripts/checks/integrity_runtime_determinism.py", 
                             compare_files=["storage/data/integration_binding_matrix_1.json", 
                                            "storage/data/integration_binding_matrix_2.json"])
print(f"Compare exit code: {compare_result.returncode}")
print(f"Compare stdout: {compare_result.stdout}")
print(f"Compare stderr: {compare_result.stderr}")
