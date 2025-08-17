from typing import Callable, NotRequired

from Component.Structure.IterableStructureComponent import (
    IterableStructureComponent,
    IterableStructureTypedDict,
)
from Structure.StructureTypes.MappingStructure import MappingStructure
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class MappingStructureTypedDict(IterableStructureTypedDict):
    min_key_similarity_threshold: NotRequired[float]
    min_value_similarity_threshold: NotRequired[float]

SIMILARITY_THRESHOLD_FUNCTION:Callable[[str, float], tuple[bool, str]] = lambda key, value: (value >= 0 and value <= 1, f"{key} must be between 0 and 1")

class MappingStructureComponent[R: MappingStructure, P: MappingStructureTypedDict](IterableStructureComponent[R, P]):

    type_name = "Mapping"
    object_type = MappingStructure
    abstract = True

    default_this_types = (dict,)
    default_key_types = (str,)
    type_verifier = IterableStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("min_key_similarity_threshold", False, float, function=SIMILARITY_THRESHOLD_FUNCTION),
        TypedDictKeyTypeVerifier("min_value_similarity_threshold", False, float, function=SIMILARITY_THRESHOLD_FUNCTION),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_mapping_structure(
            min_key_similarity_threshold=fields.get("min_key_similarity_threshold", self.final.MIN_KEY_SIMILARITY_THRESHOLD),
            min_value_similarity_threshold=fields.get("min_value_similarity_threshold", self.final.MIN_VALUE_SIMILARITY_THRESHOLD),
        )
