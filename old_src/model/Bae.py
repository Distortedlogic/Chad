from bayes_opt import BayesianOptimization


class Bae:
    settings = dict(
        EXPR_MIN=30,
        EXPR_MAX=70,
        MAX_IND_SIZE=80,
        POP_SIZE=1000,
        CXPB=0.5,
        MUTPB=0.7,
        TOURNAMENT_SIZE=2,
    )

    def __init__(self):
        opt = BayesianOptimization("function", {"hyperparam": (-2, 10)})
        opt.maximize(init_points=2, n_iter=100, acq="ei")
