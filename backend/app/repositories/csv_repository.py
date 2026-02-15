from pathlib import Path

import pandas as pd

from app.core.errors import ResourceNotFoundError


class CSVRepository:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)

    def load(self, dataset_prefix: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        experiments_path = self.data_dir / f"{dataset_prefix}data.csv"
        metadata_path = self.data_dir / f"{dataset_prefix}meta.csv"

        if not experiments_path.exists() or not metadata_path.exists():
            raise ResourceNotFoundError(
                f"Dataset '{dataset_prefix}' not found. Expected files: {experiments_path.name}, {metadata_path.name}"
            )

        experiments_df = pd.read_csv(experiments_path)
        metadata_df = pd.read_csv(metadata_path)
        return experiments_df, metadata_df
