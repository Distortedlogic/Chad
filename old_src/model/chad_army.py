
from typing import Optional

from arrow import now
from IPython.core.display import clear_output

from old_src import DEBUG, FRESH, LOG_BEST_EVERY, NGEN, TOURNAMENT_SIZE
from old_src.api.dataframe import display_df
from old_src.api.graphing import graph, plot_trades, revenue_bars
from old_src.model.chad import Chad
from old_src.model.checkpoint import Checkpoint
from old_src.model.individual import Individual
from old_src.model.logbook import Logbook
from old_src.model.toolbox import ToolBox


class ChadArmy:
    def __init__(self):
        keypress = input("clear checkpoint save?")
        if keypress == "y":
            Checkpoint.clear()
        self.cp = Checkpoint.load(FRESH)
        self.cp.now = now()
        self.logbook = Logbook.load(self.cp.uuid)
        self.chad = Chad(**self.cp.chad_kwargs)
        self.toolbox = ToolBox(evaluate=self.chad.fitness, **self.cp.toolbox_kwargs)
        if FRESH:
            self.logbook.clear_book(self.cp.uuid)
            self.cp.num_changed = self.toolbox.evaluate_pop(self.cp.population)
            _ = self.cp.hall_of_fame.update(self.cp.population)
        self.log()
        self.stats_checker: Optional[str] = None

    def war(self):
        for self.cp.generation in range(self.cp.generation + 1, NGEN + 1):
            self.prev_population = self.cp.population
            self.cp.population, self.cp.num_changed = self.toolbox.standard_step(self.cp.population)
            self.post_round_process()
            if DEBUG:
                self.print_stats()
                start_awaiting_input_time = now()
                keypress = input("'s' for select")
                self.cp.now += now()-start_awaiting_input_time
                if keypress != "s":
                    continue
            if self.cp.generation % LOG_BEST_EVERY == 0:
                self.print_stats()
                if self.stats_checker != "q":
                    start_awaiting_input_time = now()
                    self.stats_checker = input("press key to continue, q - run forever")
                    self.cp.now += now()-start_awaiting_input_time
            if self.cp.generation % 5 == 0:
                self.cp.population = self.toolbox.selDoubleTournament(self.cp.population, self.cp.pop_size, TOURNAMENT_SIZE)
            else:
                self.cp.population = self.toolbox.selTournament(self.cp.population, self.cp.pop_size, TOURNAMENT_SIZE)

    def log(self):
        self.logbook.log(self.cp)
        self.logbook.display(clear=not DEBUG)
        self.logbook.save()

    def post_round_process(self):
        self.cp.hall_of_fame.update(self.cp.population)
        self.cp.checkpoint()
        self.log()

    def print_stats(self):
        if not DEBUG:
            clear_output()
        else:
            if self.prev_population == self.cp.population:
                print("Population did not change")
        best: Individual = self.cp.hall_of_fame[0]
        graph(best)
        _ = self.chad.fitness(best)
        history = self.chad.history
        close = self.chad.close
        if len(history) == 0:
            print("no trades made")
            return
        self.chad.print_results()
        revenue_bars(history)
        plot_trades(close, history)
        display_df(history)
