from inspect import isgenerator
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

from promplate.chain.node import Context, Interruptable, resolve

from ._common import CallableWrapper

Function = TypeVar("Function", bound=Callable[[Context], Any])


class SimpleNode(CallableWrapper[Function], Interruptable):
    def __init__(self, function):
        super().__init__(function)
        self.callbacks = []

    _context = None

    def _invoke(self, context, /, complete, callbacks, **config):
        for _ in self._stream(context, None, callbacks):
            ...

    async def _ainvoke(self, context, /, complete, callbacks, **config):
        async for _ in self._astream(context, None, callbacks):
            ...

    def _stream(self, context, /, generate, callbacks, **config):
        self._apply_pre_processes(context, callbacks)

        ret = self.__call__(context)

        if isgenerator(ret):
            for i in ret:
                context.result = i
                self._apply_mid_processes(context, callbacks)
                yield
        else:
            context.result = ret
            self._apply_mid_processes(context, callbacks)
            yield

        self._apply_end_processes(context, callbacks)

    async def _astream(self, context, /, generate, callbacks, **config):
        await self._apply_async_pre_processes(context, callbacks)

        ret = await resolve(resolve(self.__call__(context)))

        if "__aiter__" in dir(ret):
            async for i in ret:
                context.result = i
                await self._apply_async_mid_processes(context, callbacks)
                yield
        elif isgenerator(ret):
            for i in ret:
                context.result = i
                await self._apply_async_mid_processes(context, callbacks)
                yield
        else:
            context.result = ret
            await self._apply_async_mid_processes(context, callbacks)
            yield

        await self._apply_async_end_processes(context, callbacks)

    if TYPE_CHECKING:

        def invoke(self, context: Optional[Context] = None):  # type: ignore
            return super().invoke(context)

        async def ainvoke(self, context: Optional[Context] = None):  # type: ignore
            return await super().ainvoke(context)

        def stream(self, context: Optional[Context] = None):  # type: ignore
            yield from super().stream(context)

        async def astream(self, context: Optional[Context] = None):  # type: ignore
            async for i in super().astream(context):
                yield i
