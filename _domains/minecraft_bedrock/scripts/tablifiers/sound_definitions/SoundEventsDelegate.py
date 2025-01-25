from typing import Any, Sequence, cast

import Structure.Delegate.Delegate as Delegate
import Structure.DictStructure as DictStructure
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("SoundEventsDelegate",)

class SoundEventsDelegate(Delegate.Delegate[str, DictStructure.DictStructure, str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (DictStructure.DictStructure,)

    def compare_text(self, data:dict[str,Any], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, Sequence[Trace.ErrorTrace]]:
        output:list[str] = []
        exceptions:list[Trace.ErrorTrace] = []
        has_changes = False
        if self.get_structure().sorting_function is not None:
            data = cast(Any, {key: value for key, value in sorted(data.items(), key=self.get_structure().sorting_function)})
        # sound_event_name is not used. It is controlled by this Delegate's child, SoundEventDelegate
        for sound_event_name, sound_event_data in data.items():
            D.last_value(sound_event_data)["name"] = sound_event_name # make sure the diffiness is carried across correctly.

            structure, new_exceptions = self.get_structure().get_structure(sound_event_name, sound_event_data)
            exceptions.extend(exception.add(self.get_structure().name, sound_event_name) for exception in new_exceptions)
            assert structure is not None
            comparison, any_changes, new_exceptions = structure.compare_text(D.last_value(sound_event_data), environment)
            has_changes = has_changes or any_changes
            output.append(comparison)
        return "\n|-\n".join(output), has_changes, exceptions
