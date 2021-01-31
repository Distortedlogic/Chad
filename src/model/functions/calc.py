def calc_sqn(history):
    mean_profit = history["profit"].mean()
    std_profit = history["profit"].std()
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
