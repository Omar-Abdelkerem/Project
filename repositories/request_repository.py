import csv
from core.file_singleton import FileSingleton

class RequestRepository:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_manager = FileSingleton.get_instance()

    def get_all(self):
        return self.file_manager.read_csv(self.file_path)

    def update_status(self, request_id, new_status):
        """Update request status in CSV."""
        rows = []
        with open(self.file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = row.get("RequestID") or row.get("id")
                if rid == request_id:
                    if "Status" in row:
                        row["Status"] = new_status
                    else:
                        row["status"] = new_status
                rows.append(row)

        if not rows:
            return

        fieldnames = rows[0].keys()
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
