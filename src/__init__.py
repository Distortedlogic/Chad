from typing import List, Tuple

from decouple import config
from Ionomy import BitTA, IonPanda

DEBUG = True
FRESH = True
VERSION = "0.0.1"

EXPR_MIN = 10
EXPR_MAX = 20
MAX_IND_SIZE = 30
POP_SIZE = 10

CXPB = 0.5
MUTPB = 0.7
TOURNAMENT_SIZE = 25

NGEN = 1000
HOF_SIZE = 1
RND_SEED_INT = 7
LOG_BEST_EVERY = 10

MIN_NUM_TRADES = 1000
MAX_TRADE_AMOUNT = 0.1
FEE_RATE = 0.002
ALT_COINS = ["eos", "eth", "xmr"]

PAIRS: List[Tuple[str, str]] = [("btc", "usd")]
TIMEFRAME = "hour"
LIMIT = 20_000
POSITION_BOUND: float = 10*MAX_TRADE_AMOUNT

bta = BitTA(config("TREX_KEY"), config("TREX_SECRET"))
ionpd = IonPanda(config("IONOMY_KEY"), config("IONOMY_SECRET"))
