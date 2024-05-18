from inspect import getfullargspec
from typing import Awaitable, Callable, TypeVar

from promplate.chain.utils import resolve
from promplate.prompt.template import Component, Context

from ._common import CallableWrapper

MaybeAwaitableStr = str | Awaitable[str]


Function = TypeVar("Function", bound=Callable[[], MaybeAwaitableStr] | Callable[[Context], MaybeAwaitableStr])


class SimpleComponent(CallableWrapper[Function], Component):
    def __init__(self, function: Function):
        super().__init__(function)

    def render(self, context) -> str:
        if _get_positional_args_count(self.__call__):
            return self.__call__(context)  # type: ignore
        return self.__call__()  # type: ignore

    async def arender(self, context):
        return await resolve(self.render(context))


def _get_positional_args_count(func: Callable):
    return len(getfullargspec(func).args)
