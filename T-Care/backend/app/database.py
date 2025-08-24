import pandas as pd
from .config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# -----------------------------
# SQLAlchemy setup
# -----------------------------
DATABASE_URL = "sqlite:///./test.db"  # or your actual DB URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# -----------------------------
# CSV-based "database"
# -----------------------------
class CSVDatabase:
    """Simple CSV-based 'database' for development & prototyping."""

    def __init__(self, csv_path: str = settings.CSV_FILE_PATH):
        self.csv_path = csv_path
        self._data = None
        self.load_data()

    def load_data(self):
        """Load CSV into memory."""
        try:
            self._data = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at {self.csv_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading CSV: {e}")

    def get_all(self):
        """Return the whole dataset as a pandas DataFrame."""
        return self._data

    def query(self, **filters):
        """
        Filter rows based on column=value pairs.
        Example: db.query(Sex="M", Outcome="Positive")
        """
        df = self._data
        for key, value in filters.items():
            if key in df.columns:
                df = df[df[key] == value]
        return df

    def get_unique_values(self, column: str):
        """Get unique values from a column."""
        if column not in self._data.columns:
            raise ValueError(f"Column '{column}' does not exist in CSV.")
        return self._data[column].unique().tolist()


# -----------------------------
# DB session dependency (SQLAlchemy)
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Instantiate CSV "DB"
# -----------------------------
csv_db = CSVDatabase()
