#!/usr/bin/env python3
"""
Audit Trail Integration Module

Implements unified audit trail integration for M20 as specified in FR-AUDIT_TRAIL_INTEGRATION.
Integrates all verification audit trails into unified log with deterministic logging.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import uuid

class AuditTrailError(Exception):
    """Raised when audit trail integration fails."""

class IntegrationError(Exception):
    """Raised when integration failures detected."""

class TrailCorruptionError(Exception):
    """Raised when log corruption detected."""

# Expected components for integration
EXPECTED_COMPONENTS = {
    "success_criteria_protocol",
    "compliance_reporting", 
    "audit_trail_integration",
    "report_generator",
    "validation_workflow"
}

def generate_session_id() -> str:
    """Generate a unique verification session ID."""
    return str(uuid.uuid4())

def generate_timestamp() -> str:
    """Generate ISO-8601 compliant timestamp."""
    return datetime.utcnow().isoformat() + "Z"

def calculate_integrity_hash(entry_data: Dict[str, Any]) -> str:
    """Calculate SHA-256 integrity hash for audit trail entry.
    
    Args:
        entry_data: Entry data (without integrity_hash) to hash
        
    Returns:
        SHA-256 hash string
    """
    entry_json = json.dumps(entry_data, sort_keys=True).encode()
    return hashlib.sha256(entry_json).hexdigest()

def validate_trail_entry(entry: Dict[str, Any]) -> bool:
    """Validate audit trail entry against expected schema.
    
    Args:
        entry: Audit trail entry to validate
        
    Returns:
        True if entry is valid, False otherwise
    """
    try:
        # Check all required fields
        required_fields = [
            "verification_session_id",
            "component_verification",
            "timestamp",
            "verification_result",
            "integrity_hash"
        ]
        
        for field in required_fields:
            if field not in entry:
                return False
        
        # Validate field types
        if not isinstance(entry["verification_session_id"], str):
            return False
        if not isinstance(entry["component_verification"], str):
            return False
        if not isinstance(entry["timestamp"], str):
            return False
        if not isinstance(entry["verification_result"], str):
            return False
        if not isinstance(entry["integrity_hash"], str):
            return False
        
        # Validate component is one of expected
        if entry["component_verification"] not in EXPECTED_COMPONENTS:
            return False
        
        # Validate verification result values
        if entry["verification_result"] not in ["success", "failure", "warning"]:
            return False
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            return False
        
        # Validate integrity hash (SHA-256 hex string)
        integrity_hash = entry["integrity_hash"]
        if len(integrity_hash) != 64:
            return False
        
        # Verify integrity hash calculation
        entry_copy = entry.copy()
        integrity_hash_calc = entry_copy.pop("integrity_hash")
        
        entry_json = json.dumps(entry_copy, sort_keys=True)
        calculated_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        
        if calculated_hash != integrity_hash_calc:
            return False
        
        return True
        
    except (KeyError, ValueError, TypeError):
        return False

def integrate_audit_trails(source_paths: List[str]) -> List[Dict[str, Any]]:
    """Integrate multiple audit trails into unified format.
    
    Args:
        source_paths: List of paths to source audit trail files
        
    Returns:
        List of integrated audit trail entries
        
    Raises:
        IntegrationError: If integration fails
    """
    if not source_paths:
        raise IntegrationError("No source paths provided for integration")
    
    integrated_trails = []
    session_id = generate_session_id()
    
    # Process each source path
    for source_path in source_paths:
        source_path_obj = Path(source_path)
        
        if not source_path_obj.exists():
            raise IntegrationError(f"Source path does not exist: {source_path}")
        
        if source_path_obj.is_file():
            # Single file - read and validate
            try:
                with open(source_path_obj, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            entry = json.loads(line)
                            
                            if validate_trail_entry(entry):
                                integrated_entry = {
                                    "verification_session_id": session_id,
                                    "component_verification": entry.get("component_verification"),
                                    "timestamp": generate_timestamp(),
                                    "verification_result": entry.get("verification_result")
                                }
                                integrated_entry["integrity_hash"] = calculate_integrity_hash(integrated_entry)
                                integrated_trails.append(integrated_entry)
                            else:
                                # Skip invalid entries but continue processing
                                continue
                                
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines but continue processing
                            continue
                            
            except Exception as e:
                raise IntegrationError(f"Failed to read source file {source_path}: {e}")
        
        elif source_path_obj.is_dir():
            # Directory - process all JSONL files
            for jsonl_file in source_path_obj.glob("*.jsonl"):
                try:
                    with open(jsonl_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            
                            try:
                                entry = json.loads(line)
                                
                                if validate_trail_entry(entry):
                                    integrated_entry = {
                                        "verification_session_id": session_id,
                                        "component_verification": entry.get("component_verification"),
                                        "timestamp": generate_timestamp(),
                                        "verification_result": entry.get("verification_result")
                                    }
                                    integrated_entry["integrity_hash"] = calculate_integrity_hash(integrated_entry)
                                    integrated_trails.append(integrated_entry)
                                else:
                                    continue
                                    
                            except json.JSONDecodeError:
                                continue
                                
                except Exception as e:
                    raise IntegrationError(f"Failed to process directory {source_path}: {e}")
        else:
            raise IntegrationError(f"Source path is neither file nor directory: {source_path}")
    
    if not integrated_trails:
        raise IntegrationError("No valid audit trails found for integration")
    
    return integrated_trails

def write_audit_trail_entry(entry: Dict[str, Any], path: str) -> None:
    """Write audit trail entry to JSONL file.
    
    Args:
        entry: Audit trail entry to write
        path: Path to output file
        
    Raises:
        AuditTrailError: If writing fails
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Validate entry before writing
        if not validate_trail_entry(entry):
            raise AuditTrailError("Invalid audit trail entry cannot be written")
        
        # Write entry as JSONL
        with open(path, 'a') as f:
            json.dump(entry, f)
            f.write('\n')
            
    except Exception as e:
        raise AuditTrailError(f"Failed to write audit trail entry to {path}: {e}")

def validate_trail_integrity(trail_entry: Dict[str, Any]) -> bool:
    """Validate audit trail entry integrity.
    
    Args:
        trail_entry: Audit trail entry to validate
        
    Returns:
        True if entry is valid, False otherwise
    """
    return validate_trail_entry(trail_entry)

def main() -> None:
    """Main entry point for audit trail integration CLI."""
    parser = argparse.ArgumentParser(
        description="Integrate all verification audit trails into unified log"
    )
    parser.add_argument("--integrate", action="store_true", 
                       help="Integrate audit trails")
    parser.add_argument("--source", nargs="+", default=["storage/data/"],
                       help="Source directories or files for integration")
    parser.add_argument("--output", default="storage/data/verification_audit_trail.jsonl",
                       help="Output file for integrated audit trail")
    
    args = parser.parse_args()
    
    if not args.integrate:
        print("Error: --integrate flag is required")
        sys.exit(3)
    
    try:
        # Clear output file if it exists
        if os.path.exists(args.output):
            os.remove(args.output)
        
        # Integrate audit trails
        integrated_trails = integrate_audit_trails(args.source)
        
        # Write integrated trails to output file
        for entry in integrated_trails:
            write_audit_trail_entry(entry, args.output)
        
        print(f"Successfully integrated {len(integrated_trails)} audit trails to {args.output}")
        print(f"Session ID: {integrated_trails[0]['verification_session_id'] if integrated_trails else 'N/A'}")
        
        # Validate output file integrity
        if os.path.exists(args.output):
            with open(args.output, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        if not validate_trail_integrity(entry):
                            print(f"Error: Invalid entry found at line {line_num}")
                            sys.exit(3)
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON at line {line_num}")
                        sys.exit(3)
        
        sys.exit(0)
        
    except IntegrationError as e:
        print(f"Integration error: {e}")
        sys.exit(2)
    except TrailCorruptionError as e:
        print(f"Trail corruption error: {e}")
        sys.exit(3)
    except AuditTrailError as e:
        print(f"Audit trail error: {e}")
        sys.exit(3)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()