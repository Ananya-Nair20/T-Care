import csv
import os

class DataImportService:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = []

    def load_csv(self):
        """Load donor data from CSV file into memory"""
        if not os.path.exists(self.csv_path):
            print(f"Error: CSV file not found: {self.csv_path}")
            return []

        with open(self.csv_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            self.data = [row for row in reader]

        print(f"Loaded {len(self.data)} records from {self.csv_path}")
        return self.data


if __name__ == "__main__":
    # CSV inside /data/ folder
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # go up 3 levels to project root
    csv_path = os.path.join(base_dir, "data", "hackathon_data.csv")

    importer = DataImportService(csv_path)
    importer.load_csv()
