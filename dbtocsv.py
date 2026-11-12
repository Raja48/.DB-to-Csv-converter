import csv
import os
from pathlib import Path
import sqlite3


def convert_db_to_csv(input_folder: str, output_folder: str = "csv_output"):
  input_path = Path(input_folder)
  output_path = Path(output_folder)

  # Find all .db files in the input directory
  db_files = list(input_path.glob("*.db"))

  if not db_files:
    print(f"No .db files found in '{input_path.resolve()}'.")
    return

  # Create the main output directory
  output_path.mkdir(parents=True, exist_ok=True)
  print(f"Found {len(db_files)} database file(s). Starting conversion...\n")

  for db_file in db_files:
    print(f"Processing database: {db_file.name}")

    # Create a subfolder for each database to avoid table name collisions
    db_output_dir = output_path / db_file.stem
    db_output_dir.mkdir(parents=True, exist_ok=True)

    try:
      conn = sqlite3.connect(db_file)
      cursor = conn.cursor()

      # Fetch all user-created tables (excluding internal sqlite_ tables)
      cursor.execute(
          "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE"
          " 'sqlite_%';"
      )
      tables = [row[0] for row in cursor.fetchall()]

      if not tables:
        print(f"  [!] No tables found in {db_file.name}. Skipping.\n")
        conn.close()
        continue

      for table_name in tables:
        print(f"  -> Exporting table '{table_name}'...", end=" ")

        # Query all data from the current table
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()

        # Extract column headers
        headers = [description[0] for description in cursor.description]

        # Write to CSV
        csv_file_path = db_output_dir / f"{table_name}.csv"
        with open(
            csv_file_path, mode="w", newline="", encoding="utf-8"
        ) as csv_file:
          writer = csv.writer(csv_file)
          writer.writerow(headers)
          writer.writerows(rows)

        print(f"Done ({len(rows)} rows saved to {csv_file_path})")

      conn.close()
      print(f"Finished {db_file.name}\n")

    except sqlite3.Error as e:
      print(f"\n  [ERROR] Could not process {db_file.name}: {e}\n")

  print(f"All conversions complete. Files saved in: '{output_path.resolve()}'")


if __name__ == "__main__":
  # "." scans the current folder where the script is located.
  # Replace "." with a specific path like "C:/my_databases" if needed.
  SOURCE_DIRECTORY = "."
  OUTPUT_DIRECTORY = "csv_output"

  convert_db_to_csv(SOURCE_DIRECTORY, OUTPUT_DIRECTORY)