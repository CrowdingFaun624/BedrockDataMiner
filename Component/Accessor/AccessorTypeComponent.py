from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import AccessorTypeTypedDict
from Component.Field.ComponentDictField import ComponentDictField
from Component.Field.Field import Field
from Component.Field.ScriptedObjectField import ScriptedObjectField
from Component.Pattern import Pattern
from Downloader.Accessor import Accessor
from Downloader.AccessorType import AccessorType
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

ACCESSOR_TYPE_PATTERN:Pattern["AccessorTypeComponent"] = Pattern("is_accessor_type")

class AccessorTypeComponent(Component[AccessorType]):

    class_name = "AccessorType"
    my_capabilities = Capabilities(is_accessor_type=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessor_class", True, str),
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("linked_accessors", False, DictTypeVerifier(dict, str, (str, dict))),
    )

    __slots__ = (
        "accessor_class_field",
        "arguments",
        "linked_accessor_types_field",
    )

    def initialize_fields(self, data: AccessorTypeTypedDict) -> Sequence[Field]:
        self.arguments = data.get("arguments", {})

        self.accessor_class_field = ScriptedObjectField(data["accessor_class"], ("accessor_class",), subclass=Accessor)
        self.linked_accessor_types_field = ComponentDictField(data.get("linked_accessors", {}), ACCESSOR_TYPE_PATTERN, ("linked_accessors",), assume_type=self.class_name)

        return (self.accessor_class_field, self.linked_accessor_types_field)

    def create_final(self, trace:Trace) -> AccessorType:
        return AccessorType(
            name=self.name,
            full_name=self.full_name,
            arguments=self.arguments,
        )

    def link_finals(self, trace:Trace) -> None:
        self.linked_accessor_types_field.check_coverage_types(lambda component: component.accessor_class_field.object, self.accessor_class_field.object.linked_accessor_types, trace)
        self.accessor_class_field.object.class_parameters.verify(self.arguments, trace)
        self.final.link_finals(
            accessor_class=self.accessor_class_field.object,
            get_linked_accessor_types=dict(self.linked_accessor_types_field.map(lambda key, component: component.final))
        )
