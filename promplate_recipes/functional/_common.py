from operator import attrgetter
from typing import Callable, Generic, TypeVar

from promplate.prompt.utils import AutoNaming

Function = TypeVar("Function", bound=Callable)


class CallableWrapper(AutoNaming, Generic[Function]):
    def __init__(self, function: Function):
        self._func = function

    __call__: Function = property(attrgetter("_func"))  # type: ignore
