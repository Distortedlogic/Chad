def calc_sqn(history):
    q = history["revenue"].quantile(0.95)
    history = history[history["revenue"] < q]
    mean_profit = history["revenue"].mean()
    std_profit = history["revenue"].std()
    root_num_trades = len(history) ** 0.5
    amplifier = (
        root_num_trades / std_profit
        if mean_profit < 0
        else std_profit / root_num_trades
    )
    return amplifier * mean_profit


def opp_type(type):
    if type == "short":
        return "long"
    else:
        return "short"
