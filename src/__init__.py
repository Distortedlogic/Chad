from decouple import config
from Ionomy import BitTA, IonPanda

DEBUG = False
FRESH = False
VERSION = "0.0.1"

EXPR_MIN = 30
EXPR_MAX = 70
MAX_IND_SIZE = 80
POP_SIZE = 1000

CXPB = 0.5
MUTPB = 0.7
TOURNAMENT_SIZE = 2

NGEN = 1000
HOF_SIZE = 1
RND_SEED_INT = 7

MIN_NUM_TRADES = 100
MAX_TRADE_AMOUNT = 0.1
FEE_RATE = 0.002
ALT_COINS = ["eos", "eth", "xmr"]

bta = BitTA(config("TREX_KEY"), config("TREX_SECRET"))
ionpd = IonPanda(config("IONOMY_KEY"), config("IONOMY_SECRET"))
