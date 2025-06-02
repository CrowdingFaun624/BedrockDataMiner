from types import EllipsisType
from typing import Any

import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.PrimitiveDelegate as PrimitiveDelegate
import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.SoundPropertiesDelegate as SoundPropertiesDelegate
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.IterableStructure as IterableStructure
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("SoundsDelegate",)


class SoundsDelegate(Delegate.Delegate[
    ICon.ICon[SCon.SCon[int], ICon.ICon[SCon.SCon[str], Any, SoundPropertiesDelegate.SoundPropertiesTypedDict], list[SoundPropertiesDelegate.SoundPropertiesTypedDict]],
    ICon.IDon[
        Diff.Diff[SCon.SDon[int]],
        Diff.Diff[ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Any], SoundPropertiesDelegate.SoundPropertiesTypedDict, SCon.SCon[str], Any]],
        list[SoundPropertiesDelegate.SoundPropertiesTypedDict],
        SCon.SCon[int],
        ICon.ICon[SCon.SCon[str], Any, SoundPropertiesDelegate.SoundPropertiesTypedDict]
    ],
    IterableStructure.IterableStructure[int, SoundPropertiesDelegate.SoundPropertiesTypedDict, list[SoundPropertiesDelegate.SoundPropertiesTypedDict], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (IterableStructure.IterableStructure,)

    uses_versions = True

    def print_comparison(
        self,
        data: ICon.IDon[
            Diff.Diff[SCon.SDon[int]],
            Diff.Diff[ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Any], SoundPropertiesDelegate.SoundPropertiesTypedDict, SCon.SCon[str], Any]],
            list[SoundPropertiesDelegate.SoundPropertiesTypedDict],
            SCon.SCon[int],
            ICon.ICon[SCon.SCon[str], Any, SoundPropertiesDelegate.SoundPropertiesTypedDict]
        ],
        trace: Trace.Trace,
        environment: StructureEnvironment.ComparisonEnvironment
    ) -> str | EllipsisType:
        output:list[str] = []
        for index, item in data.items():
            with trace.enter_key(index, item):
                if item.length == 1:
                    upcoming_note = ""
                else:
                    change_branches = PrimitiveDelegate.get_change_branches(item)
                    upcoming_notes:list[str] = []
                    for branch_index, branch in enumerate(change_branches):
                        value = item.get(branch)
                        if branch == 0:
                            assert value is not ...
                            upcoming_notes.append(f"{{{{Until|BE {PrimitiveDelegate.get_version(change_branches[branch_index + 1], True, environment)}}}}}")
                        elif item is ...:
                            upcoming_notes.append(f"{{{{Until|BE {PrimitiveDelegate.get_version(branch, True, environment)}}}}}")
                        else:
                            upcoming_notes.append(f"{{{{Upcoming|BE {PrimitiveDelegate.get_version(branch, True, environment)}}}}}")
                    upcoming_note = f" {" ".join(upcoming_notes)}"
                structure = self.structure.get_value_structure(index.last_value.last_value, item.last_value.last_value, trace, environment[item.branch_count - 1])
                assert structure is not None
                comparison = structure.print_comparison(item.last_value, trace, environment)
                output.append(f"{comparison}{upcoming_note}")
        return "<br>".join(output)
