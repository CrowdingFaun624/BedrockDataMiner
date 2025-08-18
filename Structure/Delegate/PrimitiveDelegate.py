from types import EllipsisType
from typing import Any

from Component.ComponentFunctions import register_builtin
from Structure.Container import Con, Don
from Structure.Delegate.LineDelegate import LineDelegate, LineType
from Structure.Difference import Diff
from Structure.PrimitiveStructure import PrimitiveStructure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


@register_builtin()
class PrimitiveDelegate[DC:Con, DD:Don|Diff[Don]](LineDelegate[DC, DD, PrimitiveStructure|None]):

    __slots__ = ()

    applies_to = (PrimitiveStructure, type(None))

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("field", False, str),
        TypedDictKeyTypeVerifier("enquote_strings", False, bool),
    )

    def __init__(self, structure: PrimitiveStructure|None, keys: dict[str, Any], field:str="field", enquote_strings:bool=True) -> None:
        super().__init__(structure, keys, field, enquote_strings)

    def print_branch(self, data: DC, trace: Trace, environment: PrinterEnvironment) -> list[LineType] | EllipsisType:
        return [(0, self.stringify(data.data))]

    def print_comparison(self, data: DD, bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> list[tuple[int, str]] | EllipsisType:
        if isinstance(data, Don):
            return [(0, self.stringify(data.last_value))]
        elif data.get(0) is ...:
            return [(0, f"Added {"" if self.field is None else self.field + " "}{self.stringify(data[1].last_value)}")]
        elif data.get(1) is ...:
            return [(0, f"Removed {"" if self.field is None else self.field + " "}{self.stringify(data[0].last_value)}")]
        else:
            return [(0, f"Changed {"" if self.field is None else self.field + " "}from {self.stringify(data[0].last_value)} to {self.stringify(data[1].last_value)}")]
