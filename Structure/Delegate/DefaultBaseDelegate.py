from typing import Any

import Structure.Delegate.DefaultDelegate as DefaultDelegate
import Structure.Delegate.Delegate as Delegate
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class DefaultBaseDelegate(Delegate.Delegate[str, StructureBase.StructureBase, str]):

    applies_to = (StructureBase.StructureBase,)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
    )

    __slots__ = (
        "structure_name",
    )

    def __init__(self, structure: StructureBase.StructureBase|None, keys:dict[str,dict[str,Any]], name:str) -> None:
        super().__init__(structure, keys)
        self.structure_name = name

    def compare_text(self, data: Any, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        version1, version2, versions_between = environment.versions[0], environment.versions[1], environment.versions_between[0]
        assert version2 is not None
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version is not None and version.get_order_tag().is_development_tag and version.parent is not None:
                beta_texts[index] = f" ({version.get_order_tag().development_name} of \"{version.parent.name}\")"
        if version1 is None:
            header.append(f"Addition of \"{self.structure_name}\"{beta_texts[0]} at \"{version2.name}\"{beta_texts[1]}.")
        else:
            header.append(f"Difference of \"{self.structure_name}\" between \"{version1.name}\"{beta_texts[0]} and \"{version2.name}\"{beta_texts[1]}.")
        if len(versions_between) > 0:
            files_word = "file" if len(versions_between) == 1 else "files"
            between_word = "before" if version1 is None else "between"
            if len(versions_between) > 10:
                header.append(f"Unable to create data {files_word} for {len(versions_between)} files {between_word}.")
            elif len(versions_between) <= 10:
                header.append(f"Unable to create data files for {len(versions_between)} {files_word} {between_word}: {", ".join(f"\"{version.name}\"" for version in versions_between)}")
        header.append("")

        lines:list[DefaultDelegate.LineType]
        lines, any_changes, new_exceptions = self.get_structure().get_structure().compare_text(data, environment)
        exceptions.extend(new_exceptions)

        final = header
        final.extend("\t" * line[0] + line[1] for line in lines)

        return "\n".join(final), any_changes, exceptions
