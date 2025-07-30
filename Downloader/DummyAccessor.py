from Component.ComponentFunctions import register_builtin
from Downloader.Accessor import Accessor


@register_builtin()
class DummyAccessor(Accessor):
    "Accessor that does nothing."

    __slots__ = ()
