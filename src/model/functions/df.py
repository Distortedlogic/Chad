import pandas as pd
import pandas_ta as ta
from sqlalchemy import and_
from src import bta


def get_ohlcv_uri(sym):
    return f"src/data/ohlcv/{sym}.csv"


def load_ohlcv_df(sym, base, tf="hour", limit=20_000, fresh=False):
    try:
        pd.read_csv(get_ohlcv_uri(sym))
    except:
        bta.update(sym, base, tf, limit)
        bta.df.to_csv(get_ohlcv_uri(sym))
        return bta.df
