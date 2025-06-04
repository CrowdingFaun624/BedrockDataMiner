from types import EllipsisType
from typing import Any, cast

from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon, idon_from_list
from Structure.SimpleContainer import SCon, SDon, sdon_from_bundles
from Structure.StructureEnvironment import ComparisonEnvironment
from Structure.StructureTypes.DictStructure import DictStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

__all__ = ("SoundEventsDelegate",)

class SoundEventsDelegate(Delegate[
    ICon[SCon[str], ICon[SCon[str], Any, dict[str,Any]], dict[str,dict[str,Any]]],
    IDon[Diff[SDon[str]], Diff[IDon[Diff[SDon[str]], Diff[Any], dict[str,Any], SCon[str], Any]], dict[str,dict[str,Any]], SCon[str], ICon[SCon[str], Any, dict[str,Any]]],
    DictStructure[str, Any, dict[str,Any], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypedDictTypeVerifier()

    applies_to = (DictStructure,)

    def print_comparison(
        self,
        data: IDon[Diff[SDon[str]], Diff[IDon[Diff[SDon[str]], Diff[Any], dict[str,Any], SCon[str], Any]], dict[str,dict[str,Any]], SCon[str], ICon[SCon[str], Any, dict[str,Any]]],
        trace: Trace,
        environment: ComparisonEnvironment,
    ) -> str | EllipsisType:
        output:list[str] = []
        # the below statement sorts sound events by their most recent name.
        data_dict = {key: value for key, value in sorted(data.items(), key=lambda item: item[0].last_value.last_value)}
        # sound_event_name is not used. It is controlled by this Delegate's child, SoundEventDelegate
        for sound_event_name, sound_event_data in data_dict.items():
            with trace.enter_key(sound_event_name, sound_event_data):
                branches = [branch for bundle in sound_event_data.items.keys() for branch in bundle]
                evil_dict = {key: value for key, value in sound_event_data.last_value.items()}
                evil_dict[Diff({tuple(branches): sdon_from_bundles({tuple(branches): "name"}, environment.domain)}, False)] = sound_event_name # make sure the diffiness is carried across correctly.
                good_idon = idon_from_list(evil_dict.items(), {branch: sound_event_data[branch].get_con(branch) for branch in branches})

                structure = self.structure.get_value_structure(sound_event_name.last_value.last_value, sound_event_data.last_value.last_value, trace, environment[0])
                assert structure is not None
                comparison = structure.print_comparison(cast(Any, good_idon), trace, environment)
                if comparison is ...:
                    continue
                output.append(comparison)
        return "\n|-\n".join(output)
