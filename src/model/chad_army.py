from IPython.core.display import clear_output
from src import NGEN
from src.model.chad import Chad
from src.model.functions.display import (
    graph,
    plot_ec,
    plot_trades,
    print_history,
    profit_bar,
)
from src.model.functions.model_funcs import checkpoint_cp, load_cp
from src.model.functions.population import standard_step
from src.model.functions.stats import load_stats
from src.model.functions.toolbox import load_toolbox


class ChadArmy:
    def __init__(self, df):
        self.stats = load_stats()
        self.toolbox, self.pset = load_toolbox()
        self.chad = Chad(self.pset, df)
        self.toolbox.register("evaluate", self.chad.fitness)
        self.cp = load_cp(self.toolbox, self.stats)

    def war(self):
        for self.gen in range(1, NGEN + 1):
            self.cp["pop"] = standard_step(self.toolbox, self.cp["pop"])
            self.cp["pop"] = self.toolbox.selDoubleTournament(
                self.cp["pop"],
                len(self.cp["pop"]),
                fitness_size=len(self.cp["pop"]) // 5,
            )
            self.cp["halloffame"].update(self.cp["pop"])
            self.log()
            checkpoint_cp(self.cp)

    def log(self):
        self.logbook.record(
            gen=self.gen, **self.stats.compile(self.cp["pop"]),
        )
        print(self.logbook.stream)

    def print_stats(self):
        self.chad.fitness(self.halloffame[0])
        clear_output()
        plot_ec(self.chad.history)
        profit_bar(self.chad.history)
        plot_trades(self.df["closed"], self.chad.history)
        graph(self.halloffame[0])
        print_history(self.chad.history)
