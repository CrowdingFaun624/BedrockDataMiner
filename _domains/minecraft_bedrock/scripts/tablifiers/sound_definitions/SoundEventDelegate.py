from types import EllipsisType
from typing import Any, NotRequired, Required, TypedDict, cast

from Component.ComponentFunctions import component_function
from Structure.Container import Don
from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment
from Structure.StructureTypes.KeymapStructure import KeymapStructure
from Utilities.Exceptions import StructureUnrecognizedKeyError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier


class SoundEventTypedDict(TypedDict):
    name: Required[str]
    category: NotRequired[str]
    max_distance: NotRequired[float]
    min_distance: NotRequired[float]
    sounds: Required[dict[str,Any]]

class SoundEventDiffTypedDict(TypedDict):
    name: Required[Diff[Don[str]]]
    category: NotRequired[Diff[Don[str]]]
    max_distance: NotRequired[Diff[SDon[float]]]
    min_distance: NotRequired[Diff[SDon[float]]]
    sounds: Required[Diff[IDon[Diff[SDon[str]], Diff[Don[Any]], dict[str,Any], SCon[str], Any]]]

@component_function()
class SoundEventDelegate(Delegate[
    ICon[SCon[str], Any, SoundEventTypedDict],
    IDon[Diff[SDon[str]], Any, SoundEventTypedDict, SCon[str], Any], # uses this instead of a ICon because SoundEventsDelegate passes in a customized value. The name key messes everything up.
    KeymapStructure[str, Any, SoundEventTypedDict, Any, Any, Any, str, Any, str],
    str, Any, tuple[list[str],str,str], Any,
]):

    __slots__ = ()
    type_verifier = TypedDictTypeVerifier()

    applies_to = (KeymapStructure,)

    def print_comparison(self, data:IDon[Diff[SDon[str]], Any, SoundEventTypedDict, SCon[str], Any], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> tuple[list[str],str,str] | EllipsisType:
        data_dict:SoundEventDiffTypedDict = cast(Any, {key.last_value.last_value: value for key, value in data.items()})

        category_comparison = "–"
        if "category" in data_dict:
            with trace.enter_key("category", data_dict["category"]):
                category_structure = self.structure.get_value_structure("category", data_dict["category"].last_value.last_value, trace, environment[data_dict["category"].branch_count - 1])
                assert category_structure is not None
                category_comparison = category_structure.print_comparison(data_dict["category"], bundle, trace, environment)

        sounds_comparison = "–"
        with trace.enter_key("sounds", data_dict["sounds"].last_value.last_value):
            sounds_structure = self.structure.get_value_structure("sounds", data_dict["sounds"].last_value.last_value, trace, environment[data_dict["sounds"].branch_count - 1])
            assert sounds_structure is not None
            sounds_comparison = sounds_structure.print_comparison(data_dict["sounds"].last_value, bundle, trace, environment)

        other_comparisons:dict[str,str] = {}
        for key, value_obj in data_dict.items():
            value:Diff[Don[Any]] = cast(Any, value_obj) # stupid type inferer can't tell it's a Diff.
            if key in {"name", "category", "sounds"}: continue
            if key not in {"max_distance", "min_distance"}:
                trace.exception(StructureUnrecognizedKeyError(key))
            structure = self.structure.get_value_structure(key, value.last_value.last_value, trace, environment[value.branch_count - 1])
            assert structure is not None
            other_comparison = structure.print_comparison(value, bundle, trace, environment)
            other_comparisons[key] = f"({key} = {other_comparison})"

        sound_event_column:list[str] = list(other_comparisons.values())

        return (sound_event_column, sounds_comparison, category_comparison) if sounds_comparison is not ... and category_comparison is not ... else ...
