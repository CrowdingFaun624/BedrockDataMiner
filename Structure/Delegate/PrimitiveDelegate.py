from types import EllipsisType
from typing import Any

import Structure.Container as Con
import Structure.Delegate.LineDelegate as LineDelegate
import Structure.Difference as Diff
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class PrimitiveDelegate[DC:Con.Con, DD:Con.Don|Diff.Diff[Con.Don]](LineDelegate.LineDelegate[DC, DD, PrimitiveStructure.PrimitiveStructure|None]):

    __slots__ = ()

    applies_to = (PrimitiveStructure.PrimitiveStructure, type(None))

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("enquote_strings", False, bool),
    )

    def __init__(self, structure: PrimitiveStructure.PrimitiveStructure|None, keys: dict[str, Any], field:str="field", enquote_strings:bool=True) -> None:
        super().__init__(structure, keys, field, enquote_strings, False)

    def print_branch(self, data: DC, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> list[LineDelegate.LineType] | EllipsisType:
        return [(0, self.stringify(data.data))]

    def print_comparison(self, data: DD, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> list[tuple[int, str]] | EllipsisType:
        if isinstance(data, Con.Don):
            return [(0, self.stringify(data.last_value))]
        elif data.get(0) is ...:
            return [(0, f"Added {"" if self.field is None else self.field + " "}{self.stringify(data[1].last_value)}")]
        elif data.get(1) is ...:
            return [(0, f"Removed {"" if self.field is None else self.field + " "}{self.stringify(data[0].last_value)}")]
        else:
            return [(0, f"Changed {"" if self.field is None else self.field + " "}from {self.stringify(data[0].last_value)} to {self.stringify(data[1].last_value)}")]
