from typing import Any, Callable, Mapping

from Component.ComponentObject import ComponentObject


class Function(ComponentObject):
    """
    Changes data before a Structure looks at it.
    """

    __slots__ = (
        "arguments",
        "function",
        "trace_name",
    )

    def link_function(self, function:Callable[..., Any], arguments:Mapping[str,Any]) -> None:
        """
        :param function: A Callable that **DOES NOT** modify the original object and returns nothing.
        :param arguments: kwargs that are given to the function when this Function is called.
        """
        self.function = function
        self.arguments = arguments
        self.trace_name = self.name

    def __call__(self, data:Any) -> Any:
        """
        Calls the Function's function.

        :param data: The argument of the Function's function.
        """
        return self.function(data, **self.arguments)
