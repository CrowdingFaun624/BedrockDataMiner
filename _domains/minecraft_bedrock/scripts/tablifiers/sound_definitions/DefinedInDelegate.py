from types import EllipsisType
from typing import Any

from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.IterableStructure import IterableStructure
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

__all__ = ("DefinedInDelegate",)


class DefinedInDelegate(Delegate[
    ICon[SCon[int], SCon[str], list[str]],
    IDon[Diff[SDon[int]], Diff[SDon[str]], list[str], SCon[int], SCon[str]],
    IterableStructure[int, str, list[str], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypedDictTypeVerifier()

    applies_to = (IterableStructure,)

    def print_comparison(self, data: IDon[Diff[SDon[int]], Diff[SDon[str]], list[str], SCon[int], SCon[str]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> str | EllipsisType:
        output:list[str] = []
        for index, item in data.items():
            with trace.enter_key(index, item):
                assert index.length == 1
                assert item.length == 1 # no shallow changes allowed.
                structure = self.structure.get_value_structure(index.last_value.last_value, item.last_value.last_value, trace, environment[item.branch_count - 1])
                assert structure is not None
                structure_output = structure.print_comparison(item.last_value, bundle, trace, environment)
                if structure_output is ...:
                    continue
                output.append(structure_output)
        return f"Defined in packs {", ".join(output)}"
