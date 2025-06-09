from types import EllipsisType
from typing import Any

from _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.PrimitiveDelegate import (
    get_change_branches,
    get_version,
)
from _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.SoundPropertiesDelegate import (
    SoundPropertiesTypedDict,
)
from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.IterableStructure import IterableStructure
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

__all__ = ("SoundsDelegate",)


class SoundsDelegate(Delegate[
    ICon[SCon[int], ICon[SCon[str], Any, SoundPropertiesTypedDict], list[SoundPropertiesTypedDict]],
    IDon[
        Diff[SDon[int]],
        Diff[IDon[Diff[SDon[str]], Diff[Any], SoundPropertiesTypedDict, SCon[str], Any]],
        list[SoundPropertiesTypedDict],
        SCon[int],
        ICon[SCon[str], Any, SoundPropertiesTypedDict]
    ],
    IterableStructure[int, SoundPropertiesTypedDict, list[SoundPropertiesTypedDict], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypedDictTypeVerifier()

    applies_to = (IterableStructure,)

    uses_versions = True

    def print_comparison(
        self,
        data: IDon[
            Diff[SDon[int]],
            Diff[IDon[Diff[SDon[str]], Diff[Any], SoundPropertiesTypedDict, SCon[str], Any]],
            list[SoundPropertiesTypedDict],
            SCon[int],
            ICon[SCon[str], Any, SoundPropertiesTypedDict]
        ],
        bundle:tuple[int,...],
        trace: Trace,
        environment: ComparisonEnvironment
    ) -> str | EllipsisType:
        output:list[str] = []
        for index, item in data.items():
            with trace.enter_key(index, item):
                new_bundle = tuple(branch for bundle in item.items.keys() for branch in bundle)
                if item.length == 1:
                    upcoming_note = ""
                else:
                    change_branches = get_change_branches(item, len(environment), bundle)
                    upcoming_notes:list[str] = []
                    for branch_index, branch in enumerate(change_branches):
                        value = item.get(branch)
                        if branch == 0:
                            assert value is not ...
                            upcoming_notes.append(f"{{{{Until|BE {get_version(change_branches[branch_index + 1], True, environment)}}}}}")
                        elif item is ...:
                            upcoming_notes.append(f"{{{{Until|BE {get_version(branch, True, environment)}}}}}")
                        else:
                            upcoming_notes.append(f"{{{{Upcoming|BE {get_version(branch, True, environment)}}}}}")
                    upcoming_note = f" {" ".join(upcoming_notes)}"
                structure = self.structure.get_value_structure(index.last_value.last_value, item.last_value.last_value, trace, environment[item.branch_count - 1])
                assert structure is not None
                comparison = structure.print_comparison(item.last_value, new_bundle, trace, environment)
                output.append(f"{comparison}{upcoming_note}")
        return "<br>".join(output)
