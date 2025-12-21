import csv
import os
import time
import uuid

# Base data directory
# core/storage/csv_store.py -> core/storage -> core -> Project -> data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def get_file_path(table_name: str) -> str:
    """Maps a logical table name to the absolute CSV file path."""
    return os.path.join(DATA_DIR, f"{table_name}.csv")

def _acquire_lock(table_name: str, timeout: int = 10):
    """Creates a lock file to ensure atomic access."""
    lock_file = os.path.join(DATA_DIR, f"{table_name}.lock")
    start_time = time.time()
    while os.path.exists(lock_file):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Could not acquire lock for {table_name}")
        time.sleep(0.1)
    
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
    return lock_file

def _release_lock(lock_file: str):
    """Removes the lock file."""
    if os.path.exists(lock_file):
        os.remove(lock_file)

def read_all(table_name: str) -> list[dict]:
    """Reads all rows from the CSV file."""
    file_path = get_file_path(table_name)
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def find_by_id(table_name: str, id_field: str, id_value) -> dict | None:
    """Finds a single row by its ID field."""
    rows = read_all(table_name)
    for row in rows:
        if row.get(id_field) == str(id_value):
            return row
    return None

def filter_rows(table_name: str, **criteria) -> list[dict]:
    """Filters rows where all criteria match."""
    rows = read_all(table_name)
    filtered = []
    for row in rows:
        match = True
        for key, value in criteria.items():
            if row.get(key) != str(value):
                match = False
                break
        if match:
            filtered.append(row)
    return filtered

def _get_next_id(rows: list, id_field: str) -> int:
    """Computes the next integer ID based on the max current value."""
    max_id = 0
    for row in rows:
        try:
            curr_id = int(row.get(id_field, 0))
            if curr_id > max_id:
                max_id = curr_id
        except ValueError:
            continue
    return max_id + 1

def insert_row(table_name: str, row_dict: dict) -> dict:
    """Inserts a new row with atomic write and locking."""
    lock_file = _acquire_lock(table_name)
    try:
        file_path = get_file_path(table_name)
        rows = read_all(table_name)
        
        # Determine headers
        fieldnames = list(row_dict.keys())
        if rows:
            fieldnames = list(rows[0].keys())
        elif os.path.exists(file_path):
             with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
        
        rows.append(row_dict)
        
        # Atomic write
        temp_file = os.path.join(DATA_DIR, f"tmp_{table_name}_{uuid.uuid4()}.csv")
        with open(temp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        os.replace(temp_file, file_path)
        return row_dict
    finally:
        _release_lock(lock_file)

def update_row(table_name: str, id_field: str, id_value, updates_dict: dict) -> dict | None:
    """Updates a row atomically."""
    lock_file = _acquire_lock(table_name)
    try:
        file_path = get_file_path(table_name)
        rows = read_all(table_name)
        updated_row = None
        
        if not rows and not os.path.exists(file_path):
             return None 
        
        fieldnames = []
        if os.path.exists(file_path):
             with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames

        new_rows = []
        for row in rows:
            if row.get(id_field) == str(id_value):
                row.update(updates_dict)
                updated_row = row
            new_rows.append(row)
            
        if updated_row:
            temp_file = os.path.join(DATA_DIR, f"tmp_{table_name}_{uuid.uuid4()}.csv")
            with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(new_rows)
            os.replace(temp_file, file_path)
            
        return updated_row
    finally:
        _release_lock(lock_file)
