from typing import ClassVar


class SettingsBase:
    data_folder = "./data"
    file_path: ClassVar[str]

    @classmethod
    def load(cls):
        pass

    def save(self):
        pass


class TrainingSettings:
    DEBUG = True
    FRESH = True
    VERSION = "0.0.1"
    RND_SEED_INT = 7
    LOG_BEST_EVERY = 10


class DeapSettings:
    EXPR_MIN = 10
    EXPR_MAX = 20
    MAX_IND_SIZE = 30
    POP_SIZE = 10
    CXPB = 0.5
    MUTPB = 0.7
    TOURNAMENT_SIZE = 25
    NGEN = 1000
    HOF_SIZE = 1


class TradeSettings:
    MIN_NUM_TRADES = 1000
    MAX_TRADE_AMOUNT = 0.1
    FEE_RATE = 0.002
    POSITION_BOUND: float = 10*MAX_TRADE_AMOUNT
