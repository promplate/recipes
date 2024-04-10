from collections import defaultdict
from functools import partial

from box import Box
from promplate import Context, Template
from promplate.prompt.template import SafeChainMapContext
from promplate.prompt.utils import get_builtins


@partial(partial, default_box=True)
class SilentBox(Box):
    def __str__(self):
        return super().__str__() if len(self) else ""


class BuiltinsLayer(dict):
    def __getitem__(self, key):
        return get_builtins()[key]

    def __contains__(self, key):
        return key in get_builtins()


layers = []


def make_context(context: Context | None = None):
    if context is None:
        return SafeChainMapContext(*layers, BuiltinsLayer(), defaultdict(SilentBox))
    return SafeChainMapContext(dict(SilentBox(context)), *layers, BuiltinsLayer(), defaultdict(SilentBox))


class DotTemplate(Template):
    def render(self, context=None):
        return super().render(make_context(context))

    async def arender(self, context=None):
        return await super().arender(make_context(context))
