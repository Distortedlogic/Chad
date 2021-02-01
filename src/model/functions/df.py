from pathlib import Path

import pandas as pd
import pandas_ta as ta
from sqlalchemy import and_
from src import bta


def get_ohlcv_uri(sym):
    path = f"src/data/ohlcv/"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path + f"{sym}.csv"


def load_ohlcv_df(sym, base, tf="hour", limit=20_000):
    path = get_ohlcv_uri(sym)
    if Path(path).is_file():
        return pd.read_csv(path)
    else:
        bta.update(sym, base, tf, limit)
        bta.df.to_csv(path, index=False)
        return bta.df
