from types import EllipsisType
from typing import Any, NotRequired, Required, TypedDict, cast

import Structure.Container as Con
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTypes.KeymapStructure as KeymapStructure
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("SoundEventDelegate",)

class SoundEventTypedDict(TypedDict):
    name: Required[str]
    category: NotRequired[str]
    defined_in: NotRequired[list[str]]
    max_distance: NotRequired[float]
    min_distance: NotRequired[float]
    sounds: Required[dict[str,Any]]

class SoundEventDiffTypedDict(TypedDict):
    name: Required[Diff.Diff[Con.Don[str]]]
    category: NotRequired[Diff.Diff[Con.Don[str]]]
    defined_in: NotRequired[Diff.Diff[ICon.IDon[Diff.Diff[SCon.SDon[int]], Diff.Diff[SCon.SDon[str]], list[str], SCon.SCon[int], SCon.SCon[str]]]]
    max_distance: NotRequired[Diff.Diff[SCon.SDon[float]]]
    min_distance: NotRequired[Diff.Diff[SCon.SDon[float]]]
    sounds: Required[Diff.Diff[ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Con.Don[Any]], dict[str,Any], SCon.SCon[str], Any]]]


class SoundEventDelegate(Delegate.Delegate[
    ICon.ICon[SCon.SCon[str], Any, SoundEventTypedDict],
    ICon.IDon[Diff.Diff[SCon.SDon[str]], Any, SoundEventTypedDict, SCon.SCon[str], Any], # uses this instead of a ICon because SoundEventsDelegate passes in a customized value. The name key messes everything up.
    KeymapStructure.KeymapStructure[str, Any, SoundEventTypedDict, Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (KeymapStructure.KeymapStructure,)

    def print_comparison(self, data:ICon.IDon[Diff.Diff[SCon.SDon[str]], Any, SoundEventDiffTypedDict, SCon.SCon[str], Any], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> str | EllipsisType:
        data_dict:SoundEventDiffTypedDict = cast(Any, {key.last_value.last_value: value for key, value in data.items()})

        sound_event_comparison = "–"
        with trace.enter_key("name", data_dict["name"]):
            key_structure = self.structure.get_value_structure("name", data_dict["name"].last_value.last_value, trace, environment[data_dict["name"].branch_count - 1])
            assert key_structure is not None
            sound_event_comparison = key_structure.print_comparison(data_dict["name"], trace, environment)
        if sound_event_comparison is ...: sound_event_comparison = "–"

        category_comparison = "–"
        if "category" in data_dict:
            with trace.enter_key("category", data_dict["category"]):
                category_structure = self.structure.get_value_structure("category", data_dict["category"].last_value.last_value, trace, environment[data_dict["category"].branch_count - 1])
                assert category_structure is not None
                category_comparison = category_structure.print_comparison(data_dict["category"], trace, environment)

        sounds_comparison = "–"
        with trace.enter_key("sounds", data_dict["sounds"].last_value.last_value):
            sounds_structure = self.structure.get_value_structure("sounds", data_dict["sounds"].last_value.last_value, trace, environment[data_dict["sounds"].branch_count - 1])
            assert sounds_structure is not None
            sounds_comparison = sounds_structure.print_comparison(data_dict["sounds"].last_value, trace, environment)

        # defined_in_comparison = None
        # if "defined_in" in data_dict:
        #     with trace.enter_key("defined_in", data_dict["defined_in"].last_value.last_value):
        #         defined_in_structure = self.structure.get_value_structure("defined_in", data_dict["defined_in"].last_value.last_value, trace, environment[data_dict["defined_in"].branch_count - 1])
        #         assert defined_in_structure is not None
        #         defined_in_comparison = defined_in_structure.print_comparison(data_dict["defined_in"].last_value, trace, environment)
        # if defined_in_comparison is ...: defined_in_comparison = None

        other_comparisons:dict[str,str] = {}
        for key, value_obj in data_dict.items():
            value:Diff.Diff[Con.Don[Any]] = cast(Any, value_obj) # stupid type inferer can't tell it's a Diff.
            if key in {"name", "category", "sounds", "defined_in"}: continue
            if key not in {"max_distance", "min_distance"}:
                trace.exception(Exceptions.StructureUnrecognizedKeyError(key))
            structure = self.structure.get_value_structure(key, value.last_value.last_value, trace, environment[value.branch_count - 1])
            assert structure is not None
            other_comparison = structure.print_comparison(value, trace, environment)
            other_comparisons[key] = f"({key} = {other_comparison})"

        sound_event_column:list[str] = [sound_event_comparison]
        # if defined_in_comparison is not None:
        #     sound_event_column.append(defined_in_comparison)
        sound_event_column.extend(other_comparisons.values())

        output = f"| {"<br>".join(sound_event_column)} || {sounds_comparison} || {category_comparison}"
        return output
