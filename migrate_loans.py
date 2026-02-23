import sqlite3
import os

def migrate():
    db_path = "finance.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking columns in 'loan' table...")
    cursor.execute("PRAGMA table_info(loan)")
    columns = [row[1] for row in cursor.fetchall()]
    
    needed_columns = {
        "debt_type": "TEXT DEFAULT 'loan'",
        "term_months": "INTEGER",
        "min_payment": "FLOAT DEFAULT 0.0"
    }

    for col, definition in needed_columns.items():
        if col not in columns:
            print(f"Adding column '{col}' to 'loan' table...")
            try:
                cursor.execute(f"ALTER TABLE loan ADD COLUMN {col} {definition}")
                print(f"Column '{col}' added successfully.")
            except Exception as e:
                print(f"Error adding column '{col}': {e}")
        else:
            print(f"Column '{col}' already exists.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
