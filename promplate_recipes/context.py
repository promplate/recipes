from collections import defaultdict
from functools import partial
from pathlib import Path

from box import Box
from promplate import Context, Template
from promplate.prompt.template import SafeChainMapContext
from promplate.prompt.utils import get_builtins


class SilentBox(Box):
    def __str__(self):
        return super().__str__() if len(self) else ""

    if __debug__:

        def __call__(self, *args, **kwargs):
            print(f"{self.__class__} shouldn't be called {args = } {kwargs = }")
            return ""


SilentBox = partial(SilentBox, default_box=True)  # type: ignore


class BuiltinsLayer(dict):
    def __getitem__(self, key):
        return get_builtins()[key]

    def __contains__(self, key):
        return key in get_builtins()

    def __repr__(self):
        return "{ builtins }"


class ComponentsLayer(dict):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def __getitem__(self, key: str):
        try:
            template = DotTemplate.read(next(self.path.glob(f"**/{key}.*")))
            if not __debug__:
                self[key] = template
            return template
        except StopIteration:
            raise KeyError(key) from None

    def __repr__(self):
        return "{ components }"


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


def register_components(path: str | Path):
    layers.append(ComponentsLayer(path))
