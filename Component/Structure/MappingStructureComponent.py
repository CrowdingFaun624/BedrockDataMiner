from typing import Callable, Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Structure.IterableStructureComponent as IterableStructureComponent
import Structure.StructureTypes.MappingStructure as MappingStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

SIMILARITY_THRESHOLD_FUNCTION:Callable[[str, float], tuple[bool, str]] = lambda key, value: (value >= 0 and value <= 1, f"{key} must be between 0 and 1")

class MappingStructureComponent[a: MappingStructure.MappingStructure](IterableStructureComponent.IterableStructureComponent[a]):

    __slots__ = (
        "min_key_similarity_threshold",
        "min_value_similarity_threshold",
    )

    default_key_types_name = "str"
    type_verifier = IterableStructureComponent.IterableStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("min_key_similarity_threshold", False, float, function=SIMILARITY_THRESHOLD_FUNCTION),
        TypeVerifier.TypedDictKeyTypeVerifier("min_value_similarity_threshold", False, float, function=SIMILARITY_THRESHOLD_FUNCTION),
    ))

    def initialize_fields(self, data: ComponentTyping.MappingStructureTypedDict) -> Sequence[Field.Field]:
        fields = super().initialize_fields(data)

        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", self.structure_type.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", self.structure_type.MIN_VALUE_SIMILARITY_THRESHOLD)
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_mapping_structure(
                min_key_similarity_threshold=self.min_key_similarity_threshold,
                min_value_similarity_threshold=self.min_value_similarity_threshold,
            )
