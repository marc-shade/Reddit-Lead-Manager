import pandas as pd
import os
from pathlib import Path

class LocalStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.progress_file = self.data_dir / "progress.csv"
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(exist_ok=True)

    def load_progress(self) -> pd.DataFrame:
        """Load progress data from local storage"""
        if not self.progress_file.exists():
            return None
        
        try:
            return pd.read_csv(self.progress_file)
        except Exception as e:
            print(f"Error loading progress: {e}")
            return None

    def save_progress(self, df: pd.DataFrame):
        """Save progress data to local storage"""
        try:
            df.to_csv(self.progress_file, index=False)
        except Exception as e:
            print(f"Error saving progress: {e}")
