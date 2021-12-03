import random
import types
from itertools import product
from typing import Any, Callable, ClassVar, Dict, List, Type, TypeVar, Union

from deap.gp import PrimitiveSetTyped

T = TypeVar("T", bound="BaseTerminal")


class BaseRule:
    @staticmethod
    def get_base_terminals() -> List[Type["BaseTerminal"]]:
        raise NotImplementedError

    @classmethod
    def get_terminals(cls) -> List[Type["BaseTerminal"]]:
        terminals: List[Any] = []
        for terminal in cls.get_base_terminals():
            terminals += terminal.get_terminals()
        return terminals

    @staticmethod
    def get_primitive_data() -> List[Dict[str, Any]]:
        raise NotImplementedError

    @classmethod
    def add_primitives(cls, pset: PrimitiveSetTyped):
        for data in cls.get_primitive_data():
            func: Callable[..., Any] = data["func"]
            inputs: List[Union[type, str]] = data["inputs"]
            output: type = data["output"]
            terminals = cls.get_terminals()
            actual_inputs: List[Any] = []
            for input in inputs:
                if isinstance(input, str):
                    actual_inputs.append([
                        terminal for terminal in terminals if terminal.__name__.startswith(input)
                    ])
                else:
                    actual_inputs.append([input])
            for idx, real_input in enumerate(product(*actual_inputs)):
                pset.addPrimitive(func, list(real_input), output, func.__name__+str(idx))

    @classmethod
    def add_constants(cls, pset: PrimitiveSetTyped):
        for constant in cls.get_base_terminals():
            constant.add_constant(pset=pset)


class BaseTerminal:
    func: ClassVar[Callable[..., Any]]

    @staticmethod
    def get_name(name: str, *args: float):
        return "_".join([name]+[str(abs(arg)) for arg in args])

    @classmethod
    def class_name(cls, *args: Any, **kwargs: Any):
        return cls.get_name(cls.__name__, *args, *kwargs.values())

    @classmethod
    def ranges(cls) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @classmethod
    def class_factory(cls, **kwargs: Any):
        return type(cls.class_name(**kwargs), (type(cls),), {"func": classmethod(cls.func), **kwargs})

    @classmethod
    def add_constant(cls, pset: PrimitiveSetTyped):
        for kwargs in cls.ranges():
            assert cls.class_factory(**kwargs) == cls.class_factory(**kwargs), "it does not work"
            pset.addEphemeralConstant(cls.class_name(**kwargs),
                                      lambda: cls.func(*kwargs.values()),
                                      cls.class_factory(**kwargs))

    @classmethod
    def get_terminals(cls):
        return [cls.class_factory(**kwargs)() for kwargs in cls.ranges()]


class Offset(BaseTerminal):
    func: ClassVar[Callable[..., Any]] = random.randint
    lower: ClassVar[int]
    upper: ClassVar[int]

    @classmethod
    def ranges(cls):
        return [{"lower": 0, "upper": 10}]
