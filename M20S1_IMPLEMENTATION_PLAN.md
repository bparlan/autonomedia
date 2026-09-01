# M20S1 IMPLEMENTATION PLAN

## Summary
I have reviewed the M20S1 specification (SPEC-M20S1) and its verification protocol (VER-M20S1V.md). The test evaluation report (M20S1TE.md) shows:

- **Status**: completed
- **Exit Code**: 0 (Baseline Verified)
- **Ready for Implementation**: Yes

## Files to Implement:

1. **`scripts/checks/check_directory_structure.py`** - FR-DIR_AUDIT_SCRIPT
   - Function: `scan_repository()` - walks repository and classifies files by layer
   - Output: `storage/data/compliance_report.json` with `compliance_score` (0-100)
   - FR constants: `FR_DIR_AUDIT_SCRIPT = True`, `FR_SCHEMA_COMPLIANCE = True`

2. **`scripts/checks/validate_3layer_pattern.py`** - FR-COMPLIANCE_CHECK
   - Function: `analyze_imports()` - static AST analysis of Python imports
   - Output: `storage/data/import_validation_report.json` with binding matrix
   - FR constants: `FR_COMPLIANCE_CHECK = True`, `FR_SCHEMA_COMPLIANCE = True`

3. **`scripts/checks/verify_legacy_cleanup.py`** - FR-LEGACY_PURGE
   - Functions: `find_legacy_directories()`, `check_references()`, `execute_purge()`
   - Modes: `--dry-run` preview, `--execute` actual cleanup
   - Output: `storage/data/purge_report.json` with removal statistics
   - FR constants: `FR_LEGACY_PURGE = True`, `FR_SCHEMA_COMPLIANCE = True`

## All scripts must include:

### FR-SCHEMA_COMPLIANCE: JSON Schema Validation
- Report files must validate against defined JSON schemas
- Schema violations result in `{"error": "schema_violation", "details": ...}` and exit code 3
- Schema files: `COMPLIANCE_REPORT_SCHEMA`, `PURGE_REPORT_SCHEMA`, `INTEGRATION_BINDING_MATRIX_SCHEMA`, `REORG_AUDIT_LOG_SCHEMA`

### NFR-AUDIT_TRAIL: Audit Logging
- All file operations logged to `storage/data/reorg_audit_log.jsonl`
- Each entry: `{"timestamp": "iso", "action": "move|delete|create", "source_path": "...", "destination_path": "..."}`

### NFR-DETERMINISM: Deterministic Output
- Scripts must produce identical results on consecutive runs
- SHA-256 checksums of JSON reports must match across runs

## Test Suite Verification:
All 8 verification items from M20S1V.md:
1. VER-M20S1-001: `test_directory_structure.py` - directory compliance
2. VER-M20S1-002: `test_legacy_cleanup.py` - legacy cleanup functionality
3. VER-M20S1-003: `test_3layer_validation.py` - import boundary validation
4. VER-M20S1-004: `test_schema_compliance.py` - JSON schema validation
5. VER-M20S1-005: `test_backward_compatibility.py` - zero regression failures
6. VER-M20S1-006: `test_platform_isolation.py` - no cross-adapter imports
7. VER-M20S1-007: `test_determinism.py` - identical consecutive run output
8. VER-M20S1-008: `test_audit_trail.py` - valid JSONL audit entries

## Implementation Success Criteria:
- All scripts exit with code 0 on success
- All reports schema-valid
- 100% compliance score from directory audit
- 0 invalid imports from pattern validation
- Legacy directories purged safely
- Full test suite passes (pytest tests/ -q)
- Deterministic script behavior across multiple runs
- Complete audit trail with valid JSON entries

## Next Steps:
1. Implement the 4 scripts with FR constants and schema compliance
2. Fix `scripts/checks/__init__.py` imports to resolve circular dependencies
3. Run all scripts in dry-run mode to validate functionality
4. Execute full test suite to verify implementation
5. Generate completion report (M20S1C.md) with evidence trail

All requirements from the M20S1 specification have been clearly defined. Implementation can proceed.