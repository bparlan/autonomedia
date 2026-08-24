#!/usr/bin/env python3
# {Verification IDs: V-USECASE-GEN-01}
# {Requirement IDs: FR-USECASE_GENERATOR}
# Test Type: IMPLEMENTATION_CHECK

import subprocess, sys, os, glob

# Run generator
result = subprocess.run(['autonomedia-test', 'gen-usecases', '--src', 'src/', '--out', 'use_cases/'], capture_output=True, text=True)
if result.returncode != 0:
    print('Generator failed', result.stderr)
    sys.exit(1)
files = glob.glob('use_cases/*.yaml')
if not files:
    print('No use case files generated')
    sys.exit(2)
# Check each file has non-empty id and at least one scenario
import yaml
for f in files:
    with open(f) as fp:
        data = yaml.safe_load(fp)
    if not data.get('id'):
        print(f'Missing id in {f}')
        sys.exit(3)
    if not data.get('scenario'):
        print(f'No scenario in {f}')
        sys.exit(4)
print('All use case files valid')
sys.exit(0)
