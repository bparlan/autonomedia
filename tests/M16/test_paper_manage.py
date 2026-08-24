#!/usr/bin/env python3
# {Verification IDs: V-PAPER-MANAGE-01}
# {Requirement IDs: FR-PAPER_MANAGE_POSTING}
# Test Type: IMPLEMENTATION_CHECK

import subprocess, sys, os, glob

log_path = 'logs/testing/posting_mock.log'
# Ensure clean state
if os.path.exists(log_path):
    os.remove(log_path)

# Run in dry-run mode (should create log, no network)
result = subprocess.run(['autonomedia-test', 'run', '--mode', 'dry-run'], capture_output=True, text=True)
if result.returncode != 0:
    print('Run failed', result.stderr)
    sys.exit(1)
if not os.path.isfile(log_path):
    print('Log file not created')
    sys.exit(2)
print('Log file created successfully')
sys.exit(0)
