from types import EllipsisType
from typing import Any

import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("PrimitiveDelegate",)

def get_version(branch:int, get_parent:bool, environment:StructureEnvironment.ComparisonEnvironment) -> str:
    version = environment.versions[branch]
    assert version is not None
    if get_parent and version.order_tag.is_development_tag:
        version = version.parent
        assert version is not None
    return version.name

def get_change_branches(diff:Diff.Diff) -> list[int]:
    previous_bundle:Any = None
    output:list[int] = []
    for branch, bundle in enumerate(diff.bundles):
        if len(bundle) == 0 and previous_bundle is None:
            # if branch 0 has no value, it is not a change branch
            pass
        elif previous_bundle is not bundle:
            output.append(branch)
        # else: this is not a change branch.
        previous_bundle = bundle
    return output


class PrimitiveDelegate(Delegate.Delegate[
    SCon.SCon[Any],
    Diff.Diff[SCon.SDon[Any]],
    PrimitiveStructure.PrimitiveStructure[Any, str, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("code", False, bool),
    )

    applies_to = (PrimitiveStructure.PrimitiveStructure,)

    uses_versions = True

    def __init__(self, structure: PrimitiveStructure.PrimitiveStructure[Any, str, str], keys: dict[str, Any], code:bool=True) -> None:
        super().__init__(structure, keys)
        self.code = code

    def print_comparison(self, data: Diff.Diff[SCon.SDon[Any]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> str | EllipsisType:
        if data.length == 1:
            return self.print_branch(data.last_value.last_container, trace, environment[data.branch_count - 1])
        else:
            output:list[str] = []
            change_branches = get_change_branches(data)
            for index, branch in enumerate(change_branches):
                item = data.get(branch)
                if branch == 0:
                    assert item is not ...
                    print_output = self.structure.print_branch(item.get_con(branch), trace, environment[branch])
                    output.append(f"{print_output} {{{{Until|BE {get_version(change_branches[index + 1], True, environment)}}}}}")
                elif item is ...:
                    output.append(f" {{{{Until|BE {get_version(branch, True, environment)}}}}}")
                else:
                    print_output = self.print_branch(item.get_con(branch), trace, environment[branch])
                    output.append(f"{print_output} {{{{Upcoming|BE {get_version(branch, True, environment)}}}}}")
            return " ".join(output)

    def print_branch(self, data: SCon.SCon[Any], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> str | EllipsisType:
        match data.data:
            case bool():
                output = str(data.data).lower()
            case _:
                output = str(data.data)
        return f"<code>{output}</code>" if self.code else output
