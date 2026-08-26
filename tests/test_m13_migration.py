from src.autonomedia.database.schema import INIT_SCHEMA


def test_init_schema_has_verification_status():
    assert "verification_status" in INIT_SCHEMA
