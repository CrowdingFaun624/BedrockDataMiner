from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import SerializerTypedDict
from Component.Field.Field import Field
from Component.Field.ScriptedClassField import ScriptedClassField
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

        self.serializer_class_field = ScriptedClassField(data["serializer_class"], lambda script_set_set_set: script_set_set_set.serializer_classes, ("serializer_class",))

        return (self.serializer_class_field,)

    def create_final(self, trace:Trace) -> Serializer:
        return self.serializer_class_field.object_class(self.name, self.full_name, self.domain, self.arguments)

    def check(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            self.serializer_class_field.object_class.type_verifier.verify(self.arguments, trace)

    def finalize(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().finalize(trace)
            self.final.finalize()
