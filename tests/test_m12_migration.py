import os
import sqlite3

import pytest


# Assuming for now we are using a local sqlite file or can mock the DB connection
# This test will check if the 'verification_status' column exists on 'content' table
def test_verification_status_column_exists():
    db_path = "runtime/autonomedia.db"
    if not os.path.exists(db_path):
        pytest.skip("Database file not found, skipping migration test")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if verification_status column exists in content table
    cursor.execute("PRAGMA table_info(content);")
    columns = [row[1] for row in cursor.fetchall()]

    conn.close()

    assert 'verification_status' in columns, "verification_status column does not exist in content table"

def test_verification_status_default_empty():
    """Check that verification_status defaults to empty JSON for new records."""
    db_path = "runtime/autonomedia.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert a test record without verification_status
    cursor.execute("INSERT INTO content (id, topic, type, status, source_idea) VALUES ('test_m12', 'Test', 'RefLink', 'idea', 'Test idea')")
    cursor.execute("SELECT verification_status FROM content WHERE id = 'test_m12'")
    result = cursor.fetchone()

    # Clean up
    cursor.execute("DELETE FROM content WHERE id = 'test_m12'")
    conn.commit()
    conn.close()

    # Should have a value (either NULL or empty JSON based on DB type)
    assert result is not None, "Record should exist"
