from inspect import isclass
from random import choice, randint, random
from sys import exc_info
from typing import Any, DefaultDict, List, Optional, Tuple, cast

from deap import gp
from deap.gp import Primitive, PrimitiveSetTyped, Terminal

from old_src.api.graphing import graph


def generate_expression(pset: PrimitiveSetTyped,
                        terminal_types: List[Any],
                        min_: int,
                        max_: int,
                        type_: Optional[type] = None):
    type_ = type_ or cast(type, pset.ret)
    expr: List[Any] = []
    height = randint(min_, max_)
    stack: List[Tuple[int, type]] = [(0, type_)]
    terminals_dict = cast(DefaultDict[type, List[Terminal]], pset.terminals)
    primitives_dict = cast(DefaultDict[type, List[Primitive]], pset.primitives)
    terminal_names = [terminal.__name__ for terminal in terminal_types]
    while len(stack) != 0:
        depth, type_ = stack.pop()
        if type_.__name__ in terminal_names:
            try:
                terminal = choice(terminals_dict[type_])
            except IndexError:
                graph(gp.PrimitiveTree(expr))
                print(terminals_dict)
                print(terminals_dict[type_])
                print(type_)
                _, _, traceback = exc_info()
                raise IndexError("The gp.generate function tried to add "
                                 + "a terminal of type '%s', but there is "
                                 + "none available.").with_traceback(traceback)
            if isclass(terminal):
                terminal = terminal()
            expr.append(terminal)
        else:
            without_terminal_args = [p for p in primitives_dict[type_] if
                                     all([arg not in terminal_types for arg in p.args])]
            with_only_terminal_args = [p for p in primitives_dict[type_] if
                                       all([arg in terminal_types for arg in p.args])]
            with_mixed_args = [p for p in primitives_dict[type_]
                               if p not in without_terminal_args
                               and p not in with_only_terminal_args]
            try:
                # Might not be respected if there is a type without terminal args
                if height <= depth or (depth >= min_ and random() < pset.terminalRatio):
                    if len(with_only_terminal_args + with_mixed_args) == 0:
                        prim = choice(without_terminal_args)
                    else:
                        prim = choice(with_only_terminal_args + with_mixed_args)
                else:
                    if len(without_terminal_args + with_mixed_args) == 0:
                        prim = choice(with_only_terminal_args)
                    else:
                        prim = choice(without_terminal_args + with_mixed_args)
            except IndexError:
                graph(gp.PrimitiveTree(expr))
                print("self.terminal_types", terminal_types)
                print("primitives_dict", primitives_dict)
                print("without_terminal_args", without_terminal_args)
                print("with_only_terminal_args", with_only_terminal_args)
                print("with_mixed_args", with_mixed_args)
                print(type_)
                print("type_ in self.terminal_types", type_ in terminal_types)
                _, _, traceback = exc_info()
                raise IndexError("The gp.generate function tried to add "
                                 + "a primitive of type '%s', but there is "
                                 + "none available." % (type_,)).with_traceback(traceback)
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((depth + 1, arg))

    # graph(gp.PrimitiveTree(expr))
    return expr
