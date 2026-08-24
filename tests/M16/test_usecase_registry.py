#!/usr/bin/env python3
# {Verification IDs: V-USECASE-REG-01}
# {Requirement IDs: FR-USECASE_REGISTRY}
# Test Type: SPECIFICATION_CHECK

import sys
import yaml
import glob
import os

pattern = os.path.join('use_cases', '*.yaml')
files = glob.glob(pattern)
if not files:
    print('No use case files found')
    sys.exit(1)

required_keys = {'id', 'description', 'inputs', 'outputs'}
for f in files:
    with open(f) as fp:
        data = yaml.safe_load(fp)
    if not isinstance(data, dict):
        print(f'File {f} does not contain a mapping')
        sys.exit(2)
    missing = required_keys - data.keys()
    if missing:
        print(f'File {f} missing keys: {missing}')
        sys.exit(3)
print('All use case files valid')
sys.exit(0)
