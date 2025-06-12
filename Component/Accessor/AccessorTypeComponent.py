from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import AccessorTypeTypedDict
from Component.Field.ComponentDictField import ComponentDictField
from Component.Field.Field import Field
from Component.Field.ScriptedClassField import ScriptedClassField
from Component.Pattern import Pattern
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
        TypedDictKeyTypeVerifier("class_arguments", False, dict),
        TypedDictKeyTypeVerifier("linked_accessors", False, DictTypeVerifier(dict, str, (str, dict))),
        TypedDictKeyTypeVerifier("propagated_arguments", False, dict),
    )

    __slots__ = (
        "accessor_class_field",
        "class_arguments",
        "linked_accessor_types_field",
        "propagated_arguments",
    )

    def initialize_fields(self, data: AccessorTypeTypedDict) -> Sequence[Field]:
        self.class_arguments = data.get("class_arguments", {})
        self.propagated_arguments = data.get("propagated_arguments", {})

        self.accessor_class_field = ScriptedClassField(data["accessor_class"], lambda script_set_set_set: script_set_set_set.accessor_classes, ("accessor_class",))
        self.linked_accessor_types_field = ComponentDictField(data.get("linked_accessors", {}), ACCESSOR_TYPE_PATTERN, ("linked_accessors",), assume_type=self.class_name, assume_component_group="accessor_types")

        return (self.accessor_class_field, self.linked_accessor_types_field)

    def create_final(self, trace:Trace) -> AccessorType:
        return AccessorType(
            name=self.name,
            full_name=self.full_name,
            class_arguments=self.class_arguments,
            propagated_arguments=self.propagated_arguments,
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.linked_accessor_types_field.check_coverage_types(lambda component: component.accessor_class_field.object_class, self.accessor_class_field.object_class.linked_accessor_types, trace)
            self.accessor_class_field.object_class.class_parameters.verify(self.class_arguments, trace)
            self.final.link_finals(
                accessor_class=self.accessor_class_field.object_class,
                get_linked_accessor_types=dict(self.linked_accessor_types_field.map(lambda key, component: component.final))
            )
