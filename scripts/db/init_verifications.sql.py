
import os
import sqlite3


def migrate():
    db_path = "runtime/autonomedia.db"
    if not os.path.exists(db_path):

        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create verifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id TEXT PRIMARY KEY,
            content_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            status TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content(id)
        );
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    migrate()
