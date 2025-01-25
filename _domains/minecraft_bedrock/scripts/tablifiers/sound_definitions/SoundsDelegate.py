from typing import Sequence

import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.PrimitiveDelegate as PrimitiveDelegate
import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.SoundPropertiesDelegate as SoundPropertiesDelegate
import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("SoundsDelegate",)


class SoundsDelegate(Delegate.Delegate[str, AbstractIterableStructure.AbstractIterableStructure, str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (AbstractIterableStructure.AbstractIterableStructure,)

    def compare_text(self, data:list[SoundPropertiesDelegate.SoundPropertiesTypedDict|D.Diff[SoundPropertiesDelegate.SoundPropertiesTypedDict]], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, Sequence[Trace.ErrorTrace]]:
        output:list[str] = []
        exceptions:list[Trace.ErrorTrace] = []
        has_changes = False
        for index, item in enumerate(data):
            if isinstance(item, D.Diff):
                assert item.existing_count == 1
                branches = item.get_change_branches(include_zero=True)
                upcoming_notes:list[str] = []
                for branch_index, branch in enumerate(branches):
                    value = item.get(branch)
                    if branch == 0:
                        if item.get(branches[branch_index + 1]) is not D.NoExist:
                            upcoming_notes.append(f"{{{{Until|BE {PrimitiveDelegate.get_version(branches[branch_index + 1], True, environment)}}}}}")
                    elif value is D.NoExist:
                        upcoming_notes.append(f"{{{{Until|BE {PrimitiveDelegate.get_version(branch, True, environment)}}}}}")
                    else:
                        upcoming_notes.append(f"{{{{Upcoming|BE {PrimitiveDelegate.get_version(branch, True, environment)}}}}}")
                upcoming_note = f" {" ".join(upcoming_notes)}"
            else:
                upcoming_note = ""
            structure, new_exceptions = self.get_structure().get_structure(index, item)
            exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)
            assert structure is not None
            comparison, any_changes, new_exceptions = structure.compare_text(D.last_value(item), environment)
            has_changes = has_changes or any_changes
            output.append(f"{comparison}{upcoming_note}")
        return "<br>".join(output), has_changes, exceptions
