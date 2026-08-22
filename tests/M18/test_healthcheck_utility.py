#!/usr/bin/env python3
# {Verification IDs: VR-HCI-INTEGRATION-001}
# {Requirement IDs: FR-HEALTHCHECK_INTEGRATION}
# Test Type: UNIT_TEST

"""Test healthcheck utility _get_status_data function."""

import sys
import importlib.util


def test_healthcheck_module_exists():
    """Test healthcheck.py module can be imported."""
    spec = importlib.util.spec_from_file_location(
        "healthcheck",
        "src/autonomedia/checks/healthcheck.py"
    )
    
    if spec is None or spec.loader is None:
        print("FAIL: healthcheck.py module not found or cannot be imported")
        sys.exit(1)
    
    print("PASS: healthcheck.py module exists")


def test_get_status_data_function_exists():
    """Test _get_status_data function exists in healthcheck module."""
    spec = importlib.util.spec_from_file_location(
        "healthcheck",
        "src/autonomedia/checks/healthcheck.py"
    )
    healthcheck_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(healthcheck_module)
    
    if not hasattr(healthcheck_module, '_get_status_data'):
        print("FAIL: _get_status_data function not found in healthcheck module")
        sys.exit(1)
    
    print("PASS: _get_status_data function exists")


def test_get_status_data_returns_dict():
    """Test _get_status_data returns a dictionary."""
    spec = importlib.util.spec_from_file_location(
        "healthcheck",
        "src/autonomedia/checks/healthcheck.py"
    )
    healthcheck_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(healthcheck_module)
    
    result = healthcheck_module._get_status_data()
    
    if not isinstance(result, dict):
        print(f"FAIL: _get_status_data returned non-dict type: {type(result)}")
        sys.exit(1)
    
    print("PASS: _get_status_data returns dictionary")


def test_get_status_data_contains_required_keys():
    """Test _get_status_data returns dict with all required keys."""
    spec = importlib.util.spec_from_file_location(
        "healthcheck",
        "src/autonomedia/checks/healthcheck.py"
    )
    healthcheck_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(healthcheck_module)
    
    result = healthcheck_module._get_status_data()
    
    required_keys = ["database", "runtime", "tests", "src"]
    
    for key in required_keys:
        if key not in result:
            print(f"FAIL: Missing required key '{key}' in _get_status_data result")
            sys.exit(1)
    
    print("PASS: _get_status_data contains all required keys")


def test_get_status_data_values_are_valid():
    """Test _get_status_data values are either 'healthy' or 'unhealthy'."""
    spec = importlib.util.spec_from_file_location(
        "healthcheck",
        "src/autonomedia/checks/healthcheck.py"
    )
    healthcheck_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(healthcheck_module)
    
    result = healthcheck_module._get_status_data()
    
    valid_values = {"healthy", "unhealthy"}
    
    for key, value in result.items():
        if value not in valid_values:
            print(f"FAIL: Key '{key}' has invalid value '{value}'")
            print(f"Allowed values: {valid_values}")
            sys.exit(1)
    
    print("PASS: All _get_status_data values are valid")
