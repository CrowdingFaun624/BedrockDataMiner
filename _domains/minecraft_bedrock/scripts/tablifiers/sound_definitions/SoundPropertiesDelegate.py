from typing import Any, NotRequired, Required, TypedDict, cast

import Structure.Delegate.Delegate as Delegate
import Structure.Difference as D
import Structure.KeymapStructure as KeymapStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["SoundPropertiesDelegate"]

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

class SoundPropertiesDelegate(Delegate.Delegate[str, KeymapStructure.KeymapStructure, str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (KeymapStructure.KeymapStructure,)

    def compare_text(self, data:SoundPropertiesTypedDict, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        output:list[str] = []
        exceptions:list[Trace.ErrorTrace] = []
        has_changes = False
        if self.get_structure().sorting_function is not None:
            data = cast(Any, {key: value for key, value in sorted(data.items(), key=self.get_structure().sorting_function)})
        for key, value in data.items():
            structure, new_exceptions = self.get_structure().get_structure(D.last_value(key), D.last_value(value))
            exceptions.extend(exception.add(self.get_structure().name, key) for exception in new_exceptions)
            assert structure is not None
            key_structure = self.get_structure().key_structure
            assert key_structure is not None

            comparison, any_changes, new_exceptions = structure.compare_text(value, environment)
            has_changes = any_changes or has_changes
            exceptions.extend(exception.add(self.get_structure().name, key) for exception in new_exceptions)
            if D.last_value(key) == "name":
                output.append(comparison)
            else:
                key_object, key_branch = D.last_value_with_branch(key)
                key_comparison, new_exceptions = key_structure.print_text(key_object, environment[key_branch])
                exceptions.extend(exception.add(self.get_structure().name, key) for exception in new_exceptions)
                output.append(f"{key_comparison} = {comparison}")
        return ", ".join(output), has_changes, exceptions
