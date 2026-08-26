"""
Automated Compliance Reporting System

Implements automated compliance reporting for M20 as specified in FR-AUTOMATED_COMPLIANCE_REPORTING.
Generates unified compliance reports aggregating results from all M20 verification components.
"""

import json
import hashlib
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ReportMetadata:
    """Metadata for automated compliance reports."""
    report_id: str
    generation_timestamp: str
    source_criteria_report: str
    total_criteria_evaluated: int
    passed_criteria: int
    compliance_percentage: float

@dataclass
class LayerVerificationResult:
    """Verification result for a specific layer of M20 compliance."""
    layer_name: str
    criteria_verified: List[str]
    criteria_failed: List[str]
    layer_compliance_score: float
    verification_timestamp: str

@dataclass
class OverallComplianceAssessment:
    """Overall compliance assessment summary."""
    overall_score: float
    overall_status: str
    critical_failures: List[str]
    recommendations: List[str]
    assessment_timestamp: str

@dataclass
class AuditTrailReference:
    """Reference to audit trail entries."""
    session_id: str
    component: str
    entry_timestamp: str
    integrity_hash: str

@dataclass
class AutomatedComplianceReport:
    """Unified schema for all M20 compliance reports."""
    report_metadata: ReportMetadata
    layer_verification_results: List[LayerVerificationResult]
    overall_compliance_assessment: OverallComplianceAssessment
    audit_trail_reference: List[AuditTrailReference]
    report_version: str
    deterministic_hash: str

class ComplianceReportError(Exception):
    """Raised when compliance report generation fails."""
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        super().__init__(f"Compliance report error [{error_code}]: {message}")

COMPLIANCE_REPORT_TEMPLATES: Dict[str, str] = {
    "layer_template": """
    {
        "layer_name": "{layer_name}",
        "criteria_verified": {criteria_verified},
        "criteria_failed": {criteria_failed},
        "layer_compliance_score": {layer_compliance_score},
        "verification_timestamp": "{verification_timestamp}"
    }
    """,
    "metadata_template": """
    {
        "report_id": "{report_id}",
        "generation_timestamp": "{generation_timestamp}",
        "source_criteria_report": "{source_criteria_report}",
        "total_criteria_evaluated": {total_criteria_evaluated},
        "passed_criteria": {passed_criteria},
        "compliance_percentage": {compliance_percentage}
    }
    """
}

def generate_automated_report(criteria_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates automated compliance reports aggregating results from all M20 verification components.
    
    Args:
        criteria_results: Success criteria verification results from success_criteria_protocol.py
        
    Returns:
        Dict[str, Any]: Automated compliance report with unified schema for all M20 compliance reports
        
    Raises:
        ComplianceReportError: If report generation fails
    """
    try:
        # Extract verification data from criteria results
        verified_criteria = list(criteria_results.get("criteria_verified", {}).keys())
        failed_criteria = list(criteria_results.get("criteria_failed", {}).keys())
        
        # Calculate layer-based results
        layer_results = _calculate_layer_results(verified_criteria, failed_criteria)
        
        # Generate report metadata
        metadata = _generate_report_metadata(criteria_results, verified_criteria, failed_criteria)
        
        # Generate overall compliance assessment
        assessment = _generate_compliance_assessment(verified_criteria, failed_criteria, criteria_results)
        
        # Generate audit trail references
        audit_trail_refs = _generate_audit_trail_references(criteria_results)
        
        # Create unified report
        report = AutomatedComplianceReport(
            report_metadata=metadata,
            layer_verification_results=layer_results,
            overall_compliance_assessment=assessment,
            audit_trail_reference=audit_trail_refs,
            report_version="1.0",
            deterministic_hash=_calculate_report_hash(metadata, layer_results, assessment, audit_trail_refs)
        )
        
        return asdict(report)
        
    except Exception as e:
        raise ComplianceReportError("REPORT_GENERATION_FAILURE", f"Failed to generate automated compliance report: {e}")

def _calculate_layer_results(verified_criteria: List[str], failed_criteria: List[str]) -> List[LayerVerificationResult]:
    """Calculate verification results by layer (M20S1, M20S2, M20S3)."""
    layer_mapping = {
        "M20S1": [c for c in verified_criteria if c in ["3_LAYER_PATTERN_AUDIT", "DIRECTORY_STRUCTURE_VALIDATION", "INTEGRITY_AI_BINDING", "INTEGRITY_PLATFORM_CORE_BINDING", "INTEGRITY_WEB_DATA_BINDING", "PLATFORM_ISOLATION", "RUNTIME_DETERMINISM"]],
        "M20S2": [c for c in verified_criteria if c in ["INTEGRITY_AI_BINDING", "INTEGRITY_PLATFORM_CORE_BINDING", "INTEGRITY_WEB_DATA_BINDING", "PLATFORM_ISOLATION", "RUNTIME_DETERMINISM"]],
        "M20S3": [c for c in verified_criteria if c in ["FR-SUCCESS_CRITERIA_PROTOCOL", "FR-AUTOMATED_COMPLIANCE_REPORTING", "FR-AUDIT_TRAIL_INTEGRATION", "FR-REPORT_GENERATION", "FR-VALIDATION_WORKFLOW"]]
    }
    
    layer_results = []
    for layer_name, criteria in layer_mapping.items():
        failed_layer_criteria = [c for c in failed_criteria if c in criteria]
        layer_score = len(criteria) / (len(criteria) + len(failed_layer_criteria)) if (len(criteria) + len(failed_layer_criteria)) > 0 else 0.0
        
        layer_results.append(LayerVerificationResult(
            layer_name=layer_name,
            criteria_verified=criteria,
            criteria_failed=failed_layer_criteria,
            layer_compliance_score=layer_score,
            verification_timestamp=datetime.utcnow().isoformat()
        ))
    
    return layer_results

def _generate_report_metadata(criteria_results: Dict[str, Any], verified: List[str], failed: List[str]) -> ReportMetadata:
    """Generate report metadata from criteria results."""
    total_evaluated = len(verified) + len(failed)
    passed_count = len(verified)
    compliance_percentage = (passed_count / total_evaluated * 100) if total_evaluated > 0 else 0.0
    
    return ReportMetadata(
        report_id=str(uuid.uuid4()),
        generation_timestamp=datetime.utcnow().isoformat(),
        source_criteria_report="storage/data/success_criteria_report.json",
        total_criteria_evaluated=total_evaluated,
        passed_criteria=passed_count,
        compliance_percentage=compliance_percentage
    )

def _generate_compliance_assessment(verified: List[str], failed: List[str], criteria_results: Dict[str, Any]) -> OverallComplianceAssessment:
    """Generate overall compliance assessment."""
    overall_score = criteria_results.get("compliance_score", 0.0)
    critical_failures = list(criteria_results.get("criteria_failed", {}).keys())
    
    return OverallComplianceAssessment(
        overall_score=overall_score,
        overall_status="passed" if len(critical_failures) == 0 else "failed",
        critical_failures=critical_failures,
        recommendations=["Review failed criteria" if critical_failures else "All criteria passed"],
        assessment_timestamp=datetime.utcnow().isoformat()
    )

def _generate_audit_trail_references(criteria_results: Dict[str, Any]) -> List[AuditTrailReference]:
    """Generate audit trail references."""
    session_id = criteria_results.get("verification_session_id", str(uuid.uuid4()))
    
    return [
        AuditTrailReference(
            session_id=session_id,
            component="success_criteria_protocol",
            entry_timestamp=criteria_results.get("timestamp", datetime.utcnow().isoformat()),
            integrity_hash=hashlib.sha256(session_id.encode()).hexdigest()
        ),
        AuditTrailReference(
            session_id=session_id,
            component="compliance_reporting",
            entry_timestamp=datetime.utcnow().isoformat(),
            integrity_hash=hashlib.sha256(f"compliance_{session_id}".encode()).hexdigest()
        )
    ]

def _calculate_report_hash(metadata: ReportMetadata, layers: List[LayerVerificationResult], 
                          assessment: OverallComplianceAssessment, audit_trail: List[AuditTrailReference]) -> str:
    """Calculate deterministic hash for the report."""
    report_data = {
        "metadata": asdict(metadata),
        "layers": [asdict(layer) for layer in layers],
        "assessment": asdict(assessment),
        "audit_trail": [asdict(ref) for ref in audit_trail]
    }
    
    return hashlib.sha256(json.dumps(report_data, sort_keys=True).encode()).hexdigest()

def validate_report_integrity(report: Dict[str, Any]) -> bool:
    """
    Validates the integrity of an automated compliance report.
    
    Args:
        report: Automated compliance report dictionary
        
    Returns:
        bool: True if report is valid and integrity is maintained, False otherwise
    """
    try:
        # Verify required fields exist
        required_fields = ["report_metadata", "layer_verification_results", "overall_compliance_assessment", "audit_trail_reference"]
        for field in required_fields:
            if field not in report:
                return False
        
        # Verify deterministic hash matches calculated hash
        calculated_hash = _calculate_report_hash(
            ReportMetadata(**report["report_metadata"]),
            [LayerVerificationResult(**layer) for layer in report["layer_verification_results"]],
            OverallComplianceAssessment(**report["overall_compliance_assessment"]),
            [AuditTrailReference(**ref) for ref in report["audit_trail_reference"]]
        )
        
        if calculated_hash != report.get("deterministic_hash"):
            return False
        
        return True
        
    except Exception:
        return False

def write_compliance_report(report: Dict[str, Any], path: str) -> None:
    """
    Writes automated compliance report to specified path.
    
    Args:
        report: Automated compliance report dictionary
        path: Output file path
        
    Raises:
        ComplianceReportError: If report writing fails
    """
    try:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, sort_keys=True)
            
    except Exception as e:
        raise ComplianceReportError("REPORT_WRITE_FAILURE", f"Failed to write compliance report: {e}")