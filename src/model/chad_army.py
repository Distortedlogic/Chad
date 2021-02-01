from IPython.core.display import clear_output
from src import FRESH, NGEN, TOURNAMENT_SIZE
from src.model.chad import Chad
from src.model.functions.display import (
    graph,
    plot_ec,
    plot_trades,
    print_history,
    revenue_bars,
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
        self.cp = load_cp(self.toolbox, self.stats, FRESH)

    def war(self):
        for self.gen in range(1, NGEN + 1):
            self.cp["pop"] = standard_step(self.toolbox, self.cp["pop"])
            if NGEN % 5 == 0:
                self.cp["pop"] = self.toolbox.selDoubleTournament(
                    self.cp["pop"], self.cp["pop_size"], fitness_size=TOURNAMENT_SIZE,
                )
            else:
                self.cp["pop"] = self.toolbox.selTournament(
                    self.cp["pop"], self.cp["pop_size"], TOURNAMENT_SIZE
                )
            self.cp["hall_of_fame"].update(self.cp["pop"])
            self.log()
            checkpoint_cp(self.cp)

    def log(self):
        self.cp["logbook"].record(
            gen=self.gen, **self.stats.compile(self.cp["pop"]),
        )
        print(self.cp["logbook"].stream)

    def print_stats(self):
        self.chad.fitness(self.cp["hall_of_fame"][0])
        clear_output()
        self.chad.print_results()
        revenue_bars(self.chad.history)
        plot_trades(self.chad.df["close"], self.chad.history)
        graph(self.cp["hall_of_fame"][0])
        print_history(self.chad.history)
