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

    def __init__(self, structure: StructureBase.StructureBase|None, keys:dict[str,dict[str,Any]], name:str) -> None:
        super().__init__(structure, keys)
        self.structure_name = name

    def compare_text(self, data: Any, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        version1, version2, versions_between = environment.version1, environment.version2, environment.versions_between
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version is not None and version.get_order_tag().is_development_tag and version.parent is not None:
                beta_texts[index] = " (%s of \"%s\")" % (version.get_order_tag().development_name, version.parent.name)
        if version1 is None:
            header.append("Addition of \"%s\"%s at \"%s\"%s." % (self.structure_name, beta_texts[0], version2.name, beta_texts[1]))
        else:
            header.append("Difference of \"%s\" between \"%s\"%s and \"%s\"%s." % (self.structure_name, version1.name, beta_texts[0], version2.name, beta_texts[1]))
        if len(versions_between) > 0:
            files_word = "file" if len(versions_between) == 1 else "files"
            between_word = "before" if version1 is None else "between"
            if len(versions_between) > 10:
                header.append("Unable to create data %s for %i files %s." % (files_word, len(versions_between), between_word))
            elif len(versions_between) <= 10:
                header.append("Unable to create data files for %i %s %s: %s" % (len(versions_between), files_word, between_word, ", ".join("\"%s\"" % version.name for version in versions_between)))
        header.append("")

        lines:list[DefaultDelegate.LineType]
        lines, any_changes, new_exceptions = self.get_structure().get_structure().compare_text(data, environment)
        exceptions.extend(new_exceptions)

        final = header
        final.extend("\t" * line[0] + line[1] for line in lines)

        return "\n".join(final), any_changes, exceptions
