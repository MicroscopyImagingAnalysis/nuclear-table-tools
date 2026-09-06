"""Small stateful helpers for readable dataframe pipelines."""

from __future__ import annotations

from functools import wraps
import logging
import time
from typing import Callable

import pandas as pd


def log_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("Starting operation: %s", func.__name__)
        result = func(*args, **kwargs)
        logging.info("Finished operation: %s", func.__name__)
        return result

    return wrapper


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logging.info("%s executed in %.4f seconds", func.__name__, time.time() - start_time)
        return result

    return wrapper


def normalize_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    return df


class DataFrameOperator:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def apply_operation(self, func: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
        self.dataframe = func(self.dataframe)

    def get_dataframe(self) -> pd.DataFrame:
        return self.dataframe


class AdvancedOperator(DataFrameOperator):
    @log_operation
    @timeit
    def add_column(self, col_name: str, data) -> None:
        self.dataframe[col_name] = data

    @log_operation
    def filter_rows(self, condition_func) -> None:
        self.dataframe = self.dataframe[condition_func(self.dataframe)]


__all__ = [
    "AdvancedOperator",
    "DataFrameOperator",
    "log_operation",
    "normalize_column",
    "timeit",
]
