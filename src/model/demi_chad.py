from src.model.chad_army import ChadArmy
from src.model.functions.df import load_ohlcv_df


class DemiChad:
    def __init__(self):
        self.df = load_ohlcv_df("btc", "usd", tf="hour", limit=20_000)
        self.army = ChadArmy(self.df)

    def train_btc(self):
        self.army.war()
