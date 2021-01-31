from decouple import config
from Ionomy import BitTA, IonPanda

VERSION = "0.0.1"
MAX_IND_SIZE = 30
POP_SIZE = 10
CXPB = 0.5
MUTPB = 0.5

NGEN = 10
HOF_SIZE = 1
RND_SEED_INT = 7

FEE_RATE = 0.002
ALT_COINS = ["eos", "eth", "xmr"]

bta = BitTA(config("TREX_KEY"), config("TREX_SECRET"))
ionpd = IonPanda(config("IONOMY_KEY"), config("IONOMY_SECRET"))
