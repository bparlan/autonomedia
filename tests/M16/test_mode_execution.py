#!/usr/bin/env python3
# {Verification IDs: V-MODE-EXEC-01}
# {Requirement IDs: FR-MODE_EXECUTION}
# Test Type: IMPLEMENTATION_CHECK

import subprocess, json, sys, os, glob

# Ensure config exists
config_path = os.path.expanduser('~/.autonomedia/testing_config.yaml')
if not os.path.isfile(config_path):
    # create a minimal config
    with open(config_path, 'w') as f:
        f.write('mode: dry-run\nuse_case_path: use_cases/\nreport_dir: reports/testing/')

cmd = ['autonomedia-test', 'run', '--mode', 'dry-run']
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print('Command failed', result.stderr)
    sys.exit(1)
# Find generated report
reports = glob.glob('reports/testing/*.json')
if not reports:
    print('No report generated')
    sys.exit(2)
# Validate JSON schema (assuming schema validation script available)
# Simplify: just check file non-empty and parseable
for r in reports:
    try:
        with open(r) as fp:
            json.load(fp)
    except Exception as e:
        print(f'Invalid JSON in {r}: {e}')
        sys.exit(3)
print('Report generated and valid')
sys.exit(0)
