# This module contains various utilities for the pipeline stages.

# Enumerates all daily folders, yielding each folder.
# All paths are relative to base_dir
from typing import Generator
import os

def enumerate_folders(base_dir: str) -> Generator[str, None, None]
    for newspaper in os.listdir(base_dir):
        newspaper_path = os.path.join(base_dir, newspaper)
        if not os.path.isdir(newspaper_path):
            continue
        for year in os.listdir(newspaper_path):
            year_path = os.path.join(newspaper_path, year)
            if not os.path.isdir(year_path):
                continue
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                for day in os.listdir(month_path):
                    day_path = os.path.join(month_path, day)
                    if not os.path.isdir(day_path):
                        continue
                    full_day_path = os.path.join(newspaper, year, month, day)
                    yield full_day_path