from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Structure.StructureTag as StructureTag
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

TAG_PATTERN:Pattern.Pattern["StructureTagComponent"] = Pattern.Pattern("is_structure_tag")

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

    def create_final(self, trace:Trace.Trace) -> StructureTag.StructureTag:
        return StructureTag.StructureTag(
            name=self.name,
            is_file=self.is_file,
        )
