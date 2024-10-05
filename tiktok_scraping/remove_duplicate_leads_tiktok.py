import sqlite3
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Remove duplicates and matching rows from SQLite tables.")
parser.add_argument("db_path", type=str, help="Path to the SQLite database file.")
parser.add_argument("table1", type=str, help="Name of the first table (e.g., tiktok_video_1).")
parser.add_argument("table2", type=str, help="Name of the second table (e.g., tiktok_videos).")

args = parser.parse_args()

# Connect to the SQLite database
conn = sqlite3.connect(args.db_path)
cursor = conn.cursor()

# Step 1: Remove rows with duplicate 'username' in the first table, keeping only the first occurrence
cursor.execute(f"""
DELETE FROM {args.table1}
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM {args.table1}
    GROUP BY username
)
""")
conn.commit()

# Step 2: Remove rows from the first table if they exist in the second table based on 'username'
cursor.execute(f"""
DELETE FROM {args.table1}
WHERE username IN (
    SELECT username
    FROM {args.table2}
)
""")
conn.commit()

# Close the database connection
conn.close()

print(f"Duplicate rows in {args.table1} removed and matching rows between {args.table1} and {args.table2} deleted successfully.")
