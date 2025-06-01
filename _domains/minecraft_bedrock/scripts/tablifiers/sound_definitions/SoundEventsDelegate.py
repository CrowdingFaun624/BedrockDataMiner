from types import EllipsisType
from typing import Any, cast

import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.SoundEventDelegate as SoundEventDelegate
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTypes.DictStructure as DictStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("SoundEventsDelegate",)

class SoundEventsDelegate(Delegate.Delegate[
    ICon.ICon[SCon.SCon[str], ICon.ICon[SCon.SCon[str], Any, dict[str,Any]], dict[str,dict[str,Any]]],
    ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Any], dict[str,Any], SCon.SCon[str], Any]], dict[str,dict[str,Any]], SCon.SCon[str], ICon.ICon[SCon.SCon[str], Any, dict[str,Any]]],
    DictStructure.DictStructure[str, Any, dict[str,Any], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (DictStructure.DictStructure,)

    def print_comparison(
        self,
        data: ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Any], dict[str,Any], SCon.SCon[str], Any]], dict[str,dict[str,Any]], SCon.SCon[str], ICon.ICon[SCon.SCon[str], Any, dict[str,Any]]],
        trace: Trace.Trace,
        environment: StructureEnvironment.ComparisonEnvironment,
    ) -> str | EllipsisType:
        output:list[str] = []
        # the below statement sorts sound events by their most recent name.
        data_dict = {key: value for key, value in sorted(data.items(), key=lambda item: item[0].last_value.last_value)}
        # sound_event_name is not used. It is controlled by this Delegate's child, SoundEventDelegate
        for sound_event_name, sound_event_data in data_dict.items():
            with trace.enter_key(sound_event_name, sound_event_data):
                evil_dict = {key.last_value.last_value: value for key, value in sound_event_data.last_value.items()}
                evil_dict["name"] = sound_event_name # make sure the diffiness is carried across correctly.
                sound_event_data_dict:SoundEventDelegate.SoundEventDiffTypedDict = cast(Any, evil_dict)

                structure = self.structure.get_value_structure(sound_event_name.last_value.last_value, sound_event_data.last_value.last_value, trace, environment[0])
                assert structure is not None
                comparison = structure.print_comparison(cast(Any, sound_event_data_dict), trace, environment)
                if comparison is ...:
                    continue
                output.append(comparison)
        return "\n|-\n".join(output)
