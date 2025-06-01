from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentDictField as ComponentDictField
import Component.Field.Field as Field
import Component.Field.ScriptedClassField as ScriptedClassField
import Component.Pattern as Pattern
import Downloader.AccessorType as AccessorType
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent"] = Pattern.Pattern("is_accessor_type")

class AccessorTypeComponent(Component.Component[AccessorType.AccessorType]):

    class_name = "AccessorType"
    my_capabilities = Capabilities.Capabilities(is_accessor_type=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("accessor_class", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("class_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("linked_accessors", False, TypeVerifier.DictTypeVerifier(dict, str, (str, dict))),
        TypeVerifier.TypedDictKeyTypeVerifier("propagated_arguments", False, dict),
    )

    __slots__ = (
        "accessor_class_field",
        "class_arguments",
        "linked_accessor_types_field",
        "propagated_arguments",
    )

    def initialize_fields(self, data: ComponentTyping.AccessorTypeTypedDict) -> Sequence[Field.Field]:
        self.class_arguments = data.get("class_arguments", {})
        self.propagated_arguments = data.get("propagated_arguments", {})

        self.accessor_class_field = ScriptedClassField.ScriptedClassField(data["accessor_class"], lambda script_set_set_set: script_set_set_set.accessor_classes, ("accessor_class",))
        self.linked_accessor_types_field = ComponentDictField.ComponentDictField(data.get("linked_accessors", {}), ACCESSOR_TYPE_PATTERN, ("linked_accessors",), assume_type=self.class_name, assume_component_group="accessor_types")

        return (self.accessor_class_field, self.linked_accessor_types_field)

    def create_final(self, trace:Trace.Trace) -> AccessorType.AccessorType:
        return AccessorType.AccessorType(
            name=self.name,
            class_arguments=self.class_arguments,
            propagated_arguments=self.propagated_arguments,
        )

    def link_finals(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.linked_accessor_types_field.check_coverage_types(lambda component: component.accessor_class_field.object_class, self.accessor_class_field.object_class.linked_accessors, trace)
            self.accessor_class_field.object_class.class_parameters.verify(self.class_arguments, trace)
            self.final.link_finals(
                accessor_class=self.accessor_class_field.object_class,
                get_linked_accessor_types=dict(self.linked_accessor_types_field.map(lambda key, component: component.final))
            )
