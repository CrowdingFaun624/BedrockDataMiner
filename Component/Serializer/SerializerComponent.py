from types import EllipsisType
from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import SerializerTypedDict
from Component.Field.Field import Field
from Component.Field.ScriptedObjectField import ScriptedObjectField
from Component.Pattern import Pattern
from Serializer.Serializer import Serializer
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

SERIALIZER_PATTERN:Pattern["SerializerComponent"] = Pattern("is_serializer")

class SerializerComponent(Component[Serializer]):

    class_name = "Serializer"
    my_capabilities = Capabilities(is_serializer=True)
    script_referenceable = True
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("serializer_class", True, str),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    @property
    def assume_used(self) -> bool:
        return True

    __slots__ = (
        "arguments",
        "serializer_class_field",
    )

    def initialize_fields(self, data: SerializerTypedDict) -> Sequence[Field]:
        self.arguments = data.get("arguments", {})

        self.serializer_class_field = ScriptedObjectField(data["serializer_class"], ("serializer_class",), subclass=Serializer)

        return (self.serializer_class_field,)

    def create_final(self, trace:Trace) -> Serializer|EllipsisType:
        if self.serializer_class_field.object.type_verifier.verify(self.arguments, trace):
            return ...
        return self.serializer_class_field.object(self.name, self.full_name, self.domain, self.arguments)

    def finalize_component(self, trace:Trace) -> None:
        self.final.finalize()
