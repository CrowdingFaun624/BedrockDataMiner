from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import StructureTagTypedDict
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

TAG_PATTERN:Pattern["StructureTagComponent"] = Pattern("is_structure_tag")

class StructureTagComponent(Component[StructureTag]):

    class_name = "StructureTag"
    script_referenceable = True
    my_capabilities = Capabilities(is_structure_tag=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("is_file", False, bool),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "is_file",
    )

    def initialize_fields(self, data: StructureTagTypedDict) -> Sequence[Field]:
        self.is_file = data.get("is_file", False)
        return ()

    def create_final(self, trace:Trace) -> StructureTag:
        return StructureTag(
            name=self.name,
            full_name=self.full_name,
            is_file=self.is_file,
        )
