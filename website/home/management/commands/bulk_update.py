import os
import csv

# --- Configuration ---
# The CSV file with "current_name,updated_name" columns.
CSV_FILE = 'rules_documents_filename_updates.csv' 
# The directory containing the files you want to modify.
TARGET_DIRECTORY = './pages'

def create_replacement_map(csv_path):
    """Reads the CSV file and returns a dictionary of replacements."""
    replacements = {}
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader) # Skip the header row
            print(f"Reading replacements from '{csv_path}'...")
            for row in reader:
                if len(row) >= 2:
                    current_name, updated_name = row[0], row[1]
                    if current_name: # Ensure the 'find' key is not empty
                        replacements[current_name] = updated_name
    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found. Please make sure it's in the same directory as the script.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return None
        
    print(f"Found {len(replacements)} replacement rules.")
    return replacements

def update_files_in_directory(directory, replacements):
    """Walks through a directory and updates files based on the replacement map."""
    if not replacements:
        print("No replacements to perform.")
        return

    updated_files_count = 0
    # os.walk will go through the target directory and all its subdirectories
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except UnicodeDecodeError:
                # This happens if the file is not a text file (e.g., an image, pdf)
                print(f"Skipping binary file: {file_path}")
                continue
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")
                continue

            modified_content = original_content
            file_was_changed = False
            
            # Perform all replacements
            for old_text, new_text in replacements.items():
                if old_text in modified_content:
                    modified_content = modified_content.replace(old_text, new_text)
            
            # Only write back to the file if changes were actually made
            if modified_content != original_content:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    print(f"✅ Updated: {file_path}")
                    updated_files_count += 1
                except Exception as e:
                    print(f"Could not write to file {file_path}: {e}")

    print(f"\n--- Update complete! ---\nTotal files updated: {updated_files_count}")

# --- Main execution ---
if __name__ == "__main__":
    replacement_map = create_replacement_map(CSV_FILE)
    if replacement_map:
        update_files_in_directory(TARGET_DIRECTORY, replacement_map)