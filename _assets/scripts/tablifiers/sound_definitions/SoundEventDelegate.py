from typing import Any, NotRequired, Required, TypedDict, cast

import Structure.Delegate.Delegate as Delegate
import Structure.Difference as D
import Structure.KeymapStructure as KeymapStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["SoundEventDelegate"]

class SoundEventTypedDict(TypedDict):
    name: Required[str]
    category: NotRequired[str]
    defined_in: NotRequired[list[str]]
    max_distance: NotRequired[float]
    min_distance: NotRequired[float]
    sounds: Required[dict[str,Any]]


class SoundEventDelegate(Delegate.Delegate[str, KeymapStructure.KeymapStructure, str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (KeymapStructure.KeymapStructure,)

    def compare_text(self, data:SoundEventTypedDict, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        has_changes = False
        if self.get_structure().sorting_function is not None:
            data = cast(Any, {key: value for key, value in sorted(data.items(), key=self.get_structure().sorting_function)})

        key_structure, new_exceptions = self.get_structure().get_structure("name", data["name"])
        exceptions.extend(exception.add(self.get_structure().name, "name") for exception in new_exceptions)
        assert key_structure is not None
        sound_event_comparison, any_changes, new_exceptions = key_structure.compare_text(data["name"], environment)
        exceptions.extend(exception.add(self.get_structure().name, "name") for exception in new_exceptions)
        has_changes = has_changes or any_changes

        if "category" in data:
            category_structure, new_exceptions = self.get_structure().get_structure("category", data["category"])
            exceptions.extend(exception.add(self.get_structure().name, "category") for exception in new_exceptions)
            assert category_structure is not None
            category_comparison, any_changes, new_exceptions = category_structure.compare_text(data["category"], environment)
            exceptions.extend(exception.add(self.get_structure().name, "category") for exception in new_exceptions)
            has_changes = has_changes or any_changes
        else:
            category_comparison = "–"

        sounds_structure, new_exceptions = self.get_structure().get_structure("sounds", data["sounds"])
        exceptions.extend(exception.add(self.get_structure().name, "sounds") for exception in new_exceptions)
        assert sounds_structure is not None
        sounds_comparison, any_changes, new_exceptions = sounds_structure.compare_text(data["sounds"], environment)
        has_changes = has_changes or any_changes

        # if "defined_in" in data:
        #     defined_in_structure, new_exceptions = self.get_structure().get_structure("defined_in", data["defined_in"])
        #     exceptions.extend(exception.add(self.get_structure().name, "defined_in") for exception in new_exceptions)
        #     assert defined_in_structure is not None
        #     defined_in_comparison, any_changes, new_exceptions = defined_in_structure.compare_text(data["defined_in"], environment)
        #     exceptions.extend(exception.add(self.get_structure().name, "defined_in") for exception in new_exceptions)
        #     has_changes = has_changes or any_changes
        # else:
        #     defined_in_comparison = None

        other_comparisons:dict[str,str] = {}
        for key, value in data.items():
            if D.last_value(key) in {"name", "category", "sounds", "defined_in"}: continue
            if D.last_value(key) not in {"max_distance", "min_distance"}:
                exceptions.append(Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.get_structure().name, key, value))
            structure, new_exceptions = self.get_structure().get_structure(D.last_value(key), value)
            exceptions.extend(exception.add(self.get_structure().name, "defined_in") for exception in new_exceptions)
            assert structure is not None
            other_comparison, any_changes, new_exceptions = structure.compare_text(value, environment)
            exceptions.extend(exception.add(self.get_structure().name, "defined_in") for exception in new_exceptions)
            has_changes = has_changes or any_changes
            other_comparisons[D.last_value(key)] = "(%s = %s)" % (D.last_value(key), other_comparison)

        sound_event_column:list[str] = [sound_event_comparison]
        # if defined_in_comparison is not None:
        #     sound_event_column.append(defined_in_comparison)
        sound_event_column.extend(other_comparisons.values())
        
        output = "| %s || %s || %s" % ("<br>".join(sound_event_column), sounds_comparison, category_comparison)
        return output, has_changes, exceptions
