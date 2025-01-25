from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Structure.StructureTag as StructureTag
import Utilities.TypeVerifier as TypeVerifier


class StructureTagComponent(Component.Component[StructureTag.StructureTag]):

    class_name = "StructureTag"
    my_capabilities = Capabilities.Capabilities(is_structure_tag=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("is_file", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "is_file",
    )

    def initialize_fields(self, data: ComponentTyping.StructureTagTypedDict) -> Sequence[Field.Field]:
        self.is_file = data.get("is_file", False)
        return ()

    def create_final(self) -> StructureTag.StructureTag:
        return StructureTag.StructureTag(
            name=self.name,
            is_file=self.is_file,
        )

    def __hash__(self) -> int:
        return hash(self.name)
