from typing import Any

from Component.Field.Errors import Errors
from Component.Field.ListField import ListField
from Utilities.Trace import Trace


class CTypeField[T](ListField[type[T]]):
    """
    Special case of ListField that only contains types.
    """

    __slots__ = (
        "fields",
        "field_slots",
        "types",
    )

    def validate_item(self, item:Any, trace: Trace) -> Errors:
        if not isinstance(item, type):
            trace.exception(RuntimeError(f"The item is not a type, but {type(item).__name__}"))
            return self.narrow(Errors.link_final)
        return Errors.fine
