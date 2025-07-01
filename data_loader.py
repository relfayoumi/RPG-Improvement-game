import os
import re
import csv

# Removed: load_levels_from_md function is no longer needed as levels are hardcoded.

def load_quests(file_path):
    """Loads quest data from a CSV file using Python's built-in csv module."""
    if not os.path.exists(file_path):
        print(f"ERROR: Quests CSV file NOT FOUND at '{file_path}'. Please ensure the file is in the correct directory.")
        return []
    try:
        quests_list = []
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames:
                print(f"WARNING: Quests CSV file '{file_path}' appears to be empty or has no header. No quests loaded.")
                return []
            
            for row in reader:
                quests_list.append(row)
        
        if not quests_list:
            print(f"WARNING: Quests CSV file '{file_path}' is empty or contains no data rows. No quests loaded.")
            return []
            
        print(f"SUCCESS: Loaded {len(quests_list)} quests from '{file_path}'.")
        return quests_list
    except Exception as e:
        print(f"ERROR: Failed to load quests from '{file_path}'. Error details: {e}")
        return []