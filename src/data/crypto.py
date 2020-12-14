import pandas as pd
import pandas_ta as ta
from decouple import config
from Ionomy import BitTA, IonPanda
from src.session import db_engine

CURRENCY = 'btc'
BASE = 'usd'
TIME = 'hour'
LIMIT = 20_000

bta = BitTA(config('TREX_KEY'), config('TREX_SECRET'))
ionpd = IonPanda(config('IONOMY_KEY'), config('IONOMY_SECRET'))
bta.update(CURRENCY, BASE, TIME, LIMIT)
bta.df.to_sql('table_name', db_engine)
