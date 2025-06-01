from types import EllipsisType
from typing import Any, NotRequired, Required, TypedDict

import Structure.Container as Con
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTypes.KeymapStructure as KeymapStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

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

class SoundPropertiesDelegate(Delegate.Delegate[
    ICon.ICon[SCon.SCon[str], Con.Con[Any], SoundPropertiesTypedDict],
    ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Con.Don[Any]], SoundPropertiesTypedDict, SCon.SCon[str], Con.Con[Any]],
    KeymapStructure.KeymapStructure[str, Any, SoundPropertiesTypedDict, Any, str, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (KeymapStructure.KeymapStructure,)

    def print_comparison(self, data: ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[Con.Don[Any]], SoundPropertiesTypedDict, SCon.SCon[str], Con.Con[Any]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> str | EllipsisType:
        output:list[str] = []
        data_dict = {key.last_value: value for key, value in sorted(data.items(), key=lambda item: PROPERTY_ORDER[item[0].last_value.last_value])}
        key_structure = self.structure.key_structure
        assert key_structure is not None
        for key, value in data_dict.items():
            with trace.enter_key(key, value):
                structure = self.structure.get_value_structure(key.last_value, value.last_value.last_value, trace, environment[value.branch_count - 1])
                assert structure is not None

                comparison = structure.print_comparison(value, trace, environment)
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
