from types import EllipsisType
from typing import Any, cast

from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment
from Structure.StructureTypes.DictStructure import DictStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

__all__ = ("SoundEventsDelegate",)

class SoundEventsDelegate(Delegate[
    ICon[SCon[str], ICon[SCon[str], Any, dict[str,Any]], dict[str,dict[str,Any]]],
    IDon[Diff[SDon[str]], Diff[IDon[Diff[SDon[str]], Diff[Any], dict[str,Any], SCon[str], Any]], dict[str,dict[str,Any]], SCon[str], ICon[SCon[str], Any, dict[str,Any]]],
    DictStructure[str, Any, dict[str,Any], Any, Any, Any, tuple[list[str],str,str], Any, Any],
    str, Any, str, Any,
]):

    __slots__ = ()
    type_verifier = TypedDictTypeVerifier()

    applies_to = (DictStructure,)

    def print_comparison(
        self,
        data: IDon[Diff[SDon[str]], Diff[IDon[Diff[SDon[str]], Diff[Any], dict[str,Any], SCon[str], Any]], dict[str,dict[str,Any]], SCon[str], ICon[SCon[str], Any, dict[str,Any]]],
        bundle:tuple[int,...],
        trace: Trace,
        environment: ComparisonEnvironment,
    ) -> str | EllipsisType:
        output:list[str] = []
        # the below statement sorts sound events by their most recent name.
        data_dict = {key: value for key, value in sorted(data.items(), key=lambda item: item[0].last_value.last_value)}
        # sound_event_name is not used. It is controlled by this Delegate's child, SoundEventDelegate
        for sound_event_name, sound_event_data in data_dict.items():
            with trace.enter_key(sound_event_name, sound_event_data):
                new_bundle = tuple(branch for bundle in sound_event_data.items.keys() for branch in bundle)

                structure = self.structure.get_value_structure(sound_event_name.last_value.last_value, sound_event_data.last_value.last_value, trace, environment[0])
                assert structure is not None
                values_comparison:tuple[list[str],str,str]|EllipsisType = structure.print_comparison(sound_event_data.last_value, new_bundle, trace, environment)
                if values_comparison is ...:
                    continue
                sound_event_column, sounds_comparison, category_comparison = values_comparison

                sound_event_comparison = "–"
                with trace.enter_key("name", sound_event_name):
                    key_structure = self.structure.get_key_structure(sound_event_name.last_value.last_value, sound_event_data.last_value.last_value, trace, environment[sound_event_name.branch_count - 1])
                    assert key_structure is not None
                    sound_event_comparison = key_structure.print_comparison(cast(Any, sound_event_name), bundle, trace, environment)
                if sound_event_comparison is ...: sound_event_comparison = "–"
                sound_event_column.insert(0, sound_event_comparison)

                comparison = f"|{"<br>".join(sound_event_column)}||{sounds_comparison}||{category_comparison}"
                output.append(comparison)
        return "\n|-\n".join(output)
