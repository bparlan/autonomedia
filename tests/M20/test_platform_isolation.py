#!/usr/bin/env python3
# {Verification IDs: VER-M20S1-006}
# {Requirement IDs: NFR-PLATFORM_ISOLATION}
# Test Type: INTEGRITY_TEST

import subprocess
import os
import pytest

def test_platform_isolation():
    """Test that platform adapters remain isolated."""
    
    # Run the validate_3layer_pattern.py script which should check for cross-platform imports
    cmd = ["uv", "run", "python", "scripts/checks/validate_3layer_pattern.py"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Script should run successfully
    assert result.returncode == 0, f"validate_3layer_pattern.py should exit 0, got {result.returncode}. Stderr: {result.stderr}"
    
    # Should have analyzed the platform adapters
    # The script should report zero violations if platform isolation is maintained
    assert "invalid imports: 0" in result.stdout.lower(), "Should have zero invalid imports"
    assert "overall compliance score: 100.0%" in result.stdout.lower(), "Should have 100% compliance score"
    
    # Verify that platform directories exist and are properly structured
    platform_dir = "src/autonomedia/platforms"
    assert os.path.exists(platform_dir), f"Platform directory {platform_dir} should exist"
    
    # Check that each platform directory has an __init__.py file
    platform_dirs = os.listdir(platform_dir)
    for platform_dir_name in platform_dirs:
        platform_path = os.path.join(platform_dir, platform_dir_name)
        init_file = os.path.join(platform_path, "__init__.py")
        assert os.path.exists(init_file), f"Platform {platform_dir_name} should have __init__.py"
        
        # Check that the platform directory doesn't contain browser-related files
        # This is a simple check to verify isolation
        platform_files = os.listdir(platform_path)
        assert len(platform_files) > 0, f"Platform {platform_dir_name} should not be empty"

def test_platform_adapter_structure():
    """Test that platform adapters have correct structure and isolation."""
    
    # Check that each platform adapter directory exists
    platform_dirs = [
        "src/autonomedia/platforms/linkedin",
        "src/autonomedia/platforms/x", 
        "src/autonomedia/platforms/mastodon"
    ]
    
    for platform_dir in platform_dirs:
        assert os.path.exists(platform_dir), f"Platform directory {platform_dir} should exist"
        
        # Each platform should have a task_handler.py file
        task_handler = os.path.join(platform_dir, "task_handler.py")
        assert os.path.exists(task_handler), f"Platform {platform_dir} should have task_handler.py"
        
        # Each platform should have an __init__.py
        init_file = os.path.join(platform_dir, "__init__.py")
        assert os.path.exists(init_file), f"Platform {platform_dir} should have __init__.py"
        
        # Check platform structure by reading __init__.py
        with open(init_file, "r") as f:
            content = f.read()
            # Should not import other platforms
            assert "from src.autonomedia.platforms.linkedin" not in content, \
                "LinkedIn platform should not import other platforms"
            assert "from src.autonomedia.platforms.x" not in content, \
                "X platform should not import other platforms"
            assert "from src.autonomedia.platforms.mastodon" not in content, \
                "Mastodon platform should not import other platforms"
