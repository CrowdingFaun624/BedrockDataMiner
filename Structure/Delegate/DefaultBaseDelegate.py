from types import EllipsisType
from typing import Any

from Structure.Container import Con, Don
from Structure.Delegate.Delegate import Delegate
from Structure.Delegate.LineDelegate import LineType
from Structure.Difference import Diff
from Structure.StructureBase import StructureBase
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class DefaultBaseDelegate[D](Delegate[
    Con[D],
    Don[D]|Diff[Don[D]],
    StructureBase[D, list[LineType], list[LineType]],
    str, str, str, str,
]):

    applies_to = (StructureBase,)

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("name", True, str),
    )

    uses_versions = True

    __slots__ = (
        "structure_name",
    )

    def __init__(self, structure: StructureBase[D, list[LineType], list[LineType]], keys:dict[str,dict[str,Any]], name:str) -> None:
        super().__init__(structure, keys)
        self.structure_name = name

    def print_branch(self, data: Con[D], trace:Trace, environment: PrinterEnvironment) -> str|EllipsisType:
        version = environment.version
        header:list[str] = []
        if version.order_tag.is_development_tag and version.parent is not None:
            beta_text = f" ({version.order_tag.development_name} of \"{version.parent.name}\")"
        else:
            beta_text = ""
        header.append(f"Addition of \"{self.structure_name}\" at \"{version.name}\"{beta_text}.")
        header.append("")

        final = header
        if self.structure.structure is not None:
            lines = self.structure.structure.print_branch(data, trace, environment)
            if lines is ...:
                return ...
            final.extend("\t" * line[0] + line[1] for line in lines)
        return "\n".join(final)

    def print_comparison(self, data:Don[D]|Diff[Don[D]], trace:Trace, environment: ComparisonEnvironment) -> str|EllipsisType:
        version1, version2, versions_between = environment.versions[0], environment.versions[1], environment.versions_between[0]
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version.order_tag.is_development_tag and version.parent is not None:
                beta_texts[index] = f" ({version.order_tag.development_name} of \"{version.parent.name}\")"
        header.append(f"Difference of \"{self.structure_name}\" between \"{version1.name}\"{beta_texts[0]} and \"{version2.name}\"{beta_texts[1]}.")
        if len(versions_between) > 0:
            files_word = "file" if len(versions_between) == 1 else "files"
            if len(versions_between) > 10:
                header.append(f"Unable to create data {files_word} for {len(versions_between)} files between.")
            elif len(versions_between) <= 10:
                header.append(f"Unable to create data files for {len(versions_between)} {files_word} between: {", ".join(f"\"{version.name}\"" for version in versions_between)}")
        header.append("")

        final = header
        if self.structure.structure is not None:
            if isinstance(data, Diff) and data.length == 1:
                lines = self.structure.structure.print_comparison(data[0], trace, environment)
            elif isinstance(data, Diff) and data.length != 1:
                assert environment.default_delegate is not None
                lines = environment.default_delegate.print_comparison(data, trace, environment)
            else:
                lines = self.structure.structure.print_comparison(data, trace, environment)
            if lines is ...:
                return ...
            final.extend("\t" * line[0] + line[1] for line in lines)
        return "\n".join(final)
