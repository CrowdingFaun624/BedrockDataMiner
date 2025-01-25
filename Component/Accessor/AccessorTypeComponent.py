from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.LinkedObjectsField as LinkedObjectsField
import Component.Field.ScriptedClassField as ScriptedClassField
import Component.Pattern as Pattern
import Downloader.AccessorType as AccessorType
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
        self.linked_accessor_types_field = LinkedObjectsField.LinkedObjectsField(data.get("linked_accessors", {}), ACCESSOR_TYPE_PATTERN, ("linked_accessors",), assume_type=self.class_name, assume_component_group="accessor_types")

        return (self.accessor_class_field, self.linked_accessor_types_field)

    def create_final(self) -> AccessorType.AccessorType:
        return AccessorType.AccessorType(
            name=self.name,
            class_arguments=self.class_arguments,
            propagated_arguments=self.propagated_arguments,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        exceptions.extend(self.linked_accessor_types_field.check_coverage_types(lambda component: component.accessor_class_field.object_class, self.accessor_class_field.object_class.linked_accessors, self))
        trace = TypeVerifier.StackTrace([(self.accessor_class_field.object_class, TypeVerifier.TraceItemType.OTHER)])
        exceptions.extend(self.accessor_class_field.object_class.class_parameters.verify(self.class_arguments, trace))
        self.final.link_finals(
            accessor_class=self.accessor_class_field.object_class,
            get_linked_accessor_types=dict(self.linked_accessor_types_field.map(lambda key, component: component.final))
        )
        return exceptions
