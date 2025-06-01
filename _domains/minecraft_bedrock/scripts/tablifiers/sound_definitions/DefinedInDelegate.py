from types import EllipsisType
from typing import Any

import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.IterableStructure as IterableStructure
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("DefinedInDelegate",)


class DefinedInDelegate(Delegate.Delegate[
    ICon.ICon[SCon.SCon[int], SCon.SCon[str], list[str]],
    ICon.IDon[Diff.Diff[SCon.SDon[int]], Diff.Diff[SCon.SDon[str]], list[str], SCon.SCon[int], SCon.SCon[str]],
    IterableStructure.IterableStructure[int, str, list[str], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (IterableStructure.IterableStructure,)

    def print_comparison(self, data: ICon.IDon[Diff.Diff[SCon.SDon[int]], Diff.Diff[SCon.SDon[str]], list[str], SCon.SCon[int], SCon.SCon[str]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> str | EllipsisType:
        output:list[str] = []
        for index, item in data.items():
            with trace.enter_key(index, item):
                assert index.length == 1
                assert item.length == 1 # no shallow changes allowed.
                structure = self.structure.get_value_structure(index.last_value.last_value, item.last_value.last_value, trace, environment[item.branch_count - 1])
                assert structure is not None
                structure_output = structure.print_comparison(item.last_value, trace, environment)
                if structure_output is ...:
                    continue
                output.append(structure_output)
        return f"Defined in packs {", ".join(output)}"
