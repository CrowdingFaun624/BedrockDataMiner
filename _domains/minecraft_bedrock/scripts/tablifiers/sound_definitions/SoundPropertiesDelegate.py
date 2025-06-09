from types import EllipsisType
from typing import Any, NotRequired, Required, TypedDict

from Structure.Container import Con, Don
from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment
from Structure.StructureTypes.KeymapStructure import KeymapStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

__all__ = ("SoundPropertiesDelegate",)

class SoundPropertiesTypedDict(TypedDict):
    name: Required[str]
    type: NotRequired[str]
    weight: NotRequired[int]
    volume: NotRequired[float]
    pitch: NotRequired[float]
    stream: NotRequired[bool]
    load_on_low_memory: NotRequired[bool]
    is3D: NotRequired[bool]
    exclude_from_pocket_platforms: NotRequired[bool]

PROPERTY_ORDER = {key: index for index, key in enumerate((
    "name",
    "type",
    "weight",
    "volume",
    "pitch",
    "stream",
    "load_on_low_memory",
    "is3D",
    "exclude_from_pocket_platforms",
))}

class SoundPropertiesDelegate(Delegate[
    ICon[SCon[str], Con[Any], SoundPropertiesTypedDict],
    IDon[Diff[SDon[str]], Diff[Don[Any]], SoundPropertiesTypedDict, SCon[str], Con[Any]],
    KeymapStructure[str, Any, SoundPropertiesTypedDict, Any, str, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypedDictTypeVerifier()

    applies_to = (KeymapStructure,)

    def print_comparison(self, data: IDon[Diff[SDon[str]], Diff[Don[Any]], SoundPropertiesTypedDict, SCon[str], Con[Any]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> str | EllipsisType:
        output:list[str] = []
        data_dict = {key.last_value: value for key, value in sorted(data.items(), key=lambda item: PROPERTY_ORDER[item[0].last_value.last_value])}
        key_structure = self.structure.key_structure
        assert key_structure is not None
        for key, value in data_dict.items():
            with trace.enter_key(key, value):
                structure = self.structure.get_value_structure(key.last_value, value.last_value.last_value, trace, environment[value.branch_count - 1])
                assert structure is not None

                new_bundle = tuple(branch for bundle in value.items.keys() for branch in bundle)
                comparison = structure.print_comparison(value, new_bundle, trace, environment)
                if comparison is ...:
                    continue
                if key.last_value == "name":
                    output.append(comparison)
                else:
                    key_comparison = key_structure.print_branch(key.get_con(value.branch_count - 1), trace, environment[value.branch_count - 1])
                    if key_comparison is ...:
                        continue
                    output.append(f"{key_comparison} = {comparison}")
        return ", ".join(output)
