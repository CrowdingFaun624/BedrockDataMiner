from typing import Any

import Structure.Delegate.Delegate as Delegate
import Structure.Difference as D
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["PrimitiveDelegate"]

def get_version(branch:int, get_parent:bool, environment:StructureEnvironment.ComparisonEnvironment) -> str:
    version = environment.versions[branch]
    assert version is not None
    if get_parent and version.order_tag.is_development_tag:
        version = version.parent
        assert version is not None
    return version.name

class PrimitiveDelegate(Delegate.Delegate[str,PrimitiveStructure.PrimitiveStructure,str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("code", "a bool", False, bool),
    )

    applies_to = (PrimitiveStructure.PrimitiveStructure,)

    def __init__(self, structure: Any|None, keys: dict[str, Any], code:bool=True) -> None:
        super().__init__(structure, keys)
        self.code = code

    def compare_text(self, data:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if isinstance(data, D.Diff):
            output:list[str] = []
            branches = data.get_change_branches(include_zero=True)
            for index, branch in enumerate(branches):
                item = data.get(branch)
                if branch == 0:
                    print_output, new_exceptions = self.print_text(item, environment[branch])
                    exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
                    output.append(f"{print_output} {{{{Until|BE {get_version(branches[index + 1], True, environment)}}}}}")
                elif item is D.NoExist:
                    output.append(f" {{{{Until|BE {get_version(branch, True, environment)}}}}}")
                else:
                    print_output, new_exceptions = self.print_text(item, environment[branch])
                    exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
                    output.append(f"{print_output} {{{{Upcoming|BE {get_version(branch, True, environment)}}}}}")
            return " ".join(output), True, []
        else:
            print_output, new_exceptions = self.print_text(data, environment[-1])
            exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
            return print_output, False, exceptions

    def print_text(self, data: Any, environment: StructureEnvironment.PrinterEnvironment) -> tuple[str, list[Trace.ErrorTrace]]:
        match data:
            case bool():
                output = str(data).lower()
            case _:
                output = str(data)
        if self.code:
            output = f"<code>{output}</code>"
        return output, []
