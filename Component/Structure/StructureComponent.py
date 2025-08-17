from typing import AbstractSet, Any, Mapping, TypedDict

from Component.Component import Component
from Structure.Structure import Structure
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace
from Utilities.TypeVerifier import ListTypeVerifier, UnionTypeVerifier


class StructureTypedDict(TypedDict):
    pass # empty, but must exist for subclassing.

def verify_types(data:Any) -> tuple[bool,str]:
    return _verify_types(data), "items must be types or lists"

def _verify_types(data:Any) -> bool:
    if isinstance(data, type): return True
    elif isinstance(data, list): return all(_verify_types(item) for item in data)
    else: return False

def verify_tags(data:Any) -> tuple[bool, str]:
    return _verify_tags(data), "items must be StructureTags or lists"

def _verify_tags(data:Any) -> bool:
    if isinstance(data, StructureTag): return True
    elif isinstance(data, list): return all(_verify_types(item) for item in data)
    else: return False

tags_type_verifier = UnionTypeVerifier(StructureTag, ListTypeVerifier(object, list, item_function=lambda item: verify_tags(item)))
types_type_verifier = UnionTypeVerifier(type, ListTypeVerifier(object, list, item_function=lambda item: verify_types(item)))

class StructureComponent[R: Structure, P: StructureTypedDict](Component[R, P]):

    type_name = "Structure"
    object_type = Structure
    abstract = True

    def get_propagating_variables(self) -> tuple[dict[str, bool], dict[str, set[object]]]:
        return {"children_has_garbage_collection": False, "cache_versions_for_delegates": False}, {"children_tags": set()}

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_structure(propagating_booleans["children_has_garbage_collection"], propagating_sets["children_tags"])
        return False
