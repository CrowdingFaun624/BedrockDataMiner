from types import EllipsisType
from typing import Any, Iterable

from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.PrimitiveStructure import PrimitiveStructure
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

__all__ = ("PrimitiveDelegate",)

def get_version(branch:int, get_parent:bool, environment:ComparisonEnvironment) -> str:
    version = environment.versions[branch]
    # assert version is not None
    if get_parent and version.order_tag.is_development_tag:
        version = version.parent
        assert version is not None
    return version.name

def pad_bundles(bundles:list[tuple[int,...]], length:int) -> Iterable[tuple[int,...]]:
    empty_tuple = () # use variable to make sure they're all "is" identical.
    yield from bundles
    yield from (empty_tuple for i in range(len(bundles), length))
    # if len(bundles) < length:

def get_change_branches(diff:Diff, length:int, top_bundle:tuple[int,...]) -> list[int]:
    previous_bundle:Any = None
    output:list[int] = []
    for branch, bundle in enumerate(pad_bundles(diff.bundles, length)):
        if len(bundle) == 0 and previous_bundle is None:
            # if branch 0 has no value, it is not a change branch
            pass
        elif branch not in top_bundle:
            pass
        elif previous_bundle is not bundle:
            output.append(branch)
        # else: this is not a change branch.
        previous_bundle = bundle
    return output

def should_be_simple(data:Diff, length:int, bundle:tuple[int,...]) -> bool:
    padded_bundles = list(pad_bundles(data.bundles, length))
    all_bundles = [padded_bundles[branch] for branch in bundle]
    bundle1 = all_bundles[0]
    return all(bundle is bundle1 for bundle in all_bundles)

class PrimitiveDelegate(Delegate[
    SCon[Any],
    Diff[SDon[Any]],
    PrimitiveStructure[Any, str, str],
    str, Any, str, Any,
]):

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("code", False, bool),
    )

    applies_to = (PrimitiveStructure,)

    uses_versions = True

    def __init__(self, structure: PrimitiveStructure[Any, str, str], keys: dict[str, Any], code:bool=True) -> None:
        super().__init__(structure, keys)
        self.code = code

    def print_comparison(self, data: Diff[SDon[Any]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> str | EllipsisType:
        if should_be_simple(data, len(environment), bundle):
            return self.print_branch(data.last_value.last_container, trace, environment[data.branch_count - 1])
        else:
            output:list[str] = []
            change_branches = get_change_branches(data, len(environment), bundle)
            for index, branch in enumerate(change_branches):
                item = data.get(branch) if branch in data else ...
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

    def print_branch(self, data: SCon[Any], trace: Trace, environment: PrinterEnvironment) -> str | EllipsisType:
        match data.data:
            case bool():
                output = str(data.data).lower()
            case _:
                output = str(data.data)
        return f"<code>{output}</code>" if self.code else output
