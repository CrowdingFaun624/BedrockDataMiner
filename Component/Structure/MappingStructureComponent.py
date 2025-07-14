from typing import Callable, Sequence

from Component.ComponentTyping import MappingStructureTypedDict
from Component.Field.Field import Field
from Component.Structure.IterableStructureComponent import IterableStructureComponent
from Structure.StructureTypes.MappingStructure import MappingStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

SIMILARITY_THRESHOLD_FUNCTION:Callable[[str, float], tuple[bool, str]] = lambda key, value: (value >= 0 and value <= 1, f"{key} must be between 0 and 1")

class MappingStructureComponent[a: MappingStructure](IterableStructureComponent[a]):

    __slots__ = (
        "min_key_similarity_threshold",
        "min_value_similarity_threshold",
    )

    default_key_types_name = "str"
    type_verifier = IterableStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("min_key_similarity_threshold", False, float, function=SIMILARITY_THRESHOLD_FUNCTION),
        TypedDictKeyTypeVerifier("min_value_similarity_threshold", False, float, function=SIMILARITY_THRESHOLD_FUNCTION),
    ))

    def initialize_fields(self, data: MappingStructureTypedDict) -> Sequence[Field]:
        fields = super().initialize_fields(data)

        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", self.structure_type.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", self.structure_type.MIN_VALUE_SIMILARITY_THRESHOLD)
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_mapping_structure(
            min_key_similarity_threshold=self.min_key_similarity_threshold,
            min_value_similarity_threshold=self.min_value_similarity_threshold,
        )
