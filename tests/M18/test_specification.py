#!/usr/bin/env python3
# {Verification IDs: VR-DBD-SOURCE-001}
# {Requirement IDs: FR-DASHBOARD_DATA_SOURCE}
# Test Type: SPECIFICATION_CHECK

"""Test that M18S2 specification contains required elements."""

import yaml
import re
import os


def test_specification_has_id():
    """Test specification frontmatter contains id field."""
    spec_path = "milestones/M18/M18S2.md"
    
    with open(spec_path, 'r') as f:
        content = f.read()
    
    # Parse frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match, "Specification missing YAML frontmatter"
    
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert 'id' in frontmatter, "Specification missing required 'id' field"
    assert frontmatter['id'] == 'SPEC-M18S2', "Specification id does not match expected value"
    

def test_specification_contains_required_fr():
    """Test specification contains FR-DASHBOARD_DATA_SOURCE requirement."""
    spec_path = "milestones/M18/M18S2.md"
    
    with open(spec_path, 'r') as f:
        content = f.read()
    
    # Check for functional requirement FR-DASHBOARD_DATA_SOURCE
    assert 'FR-DASHBOARD_DATA_SOURCE' in content, \
        "Specification missing FR-DASHBOARD_DATA_SOURCE requirement"
    

def test_specification_contains_interface_contract():
    """Test specification contains interface contract definition."""
    spec_path = "milestones/M18/M18S2.md"
    
    with open(spec_path, 'r') as f:
        content = f.read()
    
    # Check for interface contract mentions
    assert '/api/health' in content, \
        "Specification missing /api/health endpoint reference"
    
    assert 'interface contract' in content.lower(), \
        "Specification missing interface contract terminology"
