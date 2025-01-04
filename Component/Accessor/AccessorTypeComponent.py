import Component.Accessor.Field.AccessorClassField as AccessorClassField
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.LinkedObjectsField as LinkedObjectsField
import Component.Pattern as Pattern
import Downloader.Accessor as Accessor
import Downloader.AccessorType as AccessorType
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent"] = Pattern.Pattern([{"is_accessor_type": True}])

class AccessorTypeComponent(Component.Component[AccessorType.AccessorType]):

    class_name = "AccessorType"
    class_name_article = "an AccessorType"
    my_capabilities = Capabilities.Capabilities(is_accessor_type=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("class_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("linked_accessors", "a dict", False, TypeVerifier.DictTypeVerifier(dict, str, (str, dict), "a dict", "a str", "a str or dict")),
        TypeVerifier.TypedDictKeyTypeVerifier("accessor_class", "a str", True, str),
    )

    __slots__ = (
        "accessor_class_field",
        "class_arguments",
        "linked_accessor_types_field",
    )

    def initialize_fields(self, data: ComponentTyping.AccessorTypeTypedDict) -> list[Field.Field]:
        self.class_arguments = data.get("class_arguments", {})

        self.accessor_class_field = AccessorClassField.AccessorClassField(data["accessor_class"], self.domain, ["accessor_class"])
        self.linked_accessor_types_field = LinkedObjectsField.LinkedObjectsField(data.get("linked_accessors", {}), ACCESSOR_TYPE_PATTERN, ["linked_accessors"], allow_inline=Field.InlinePermissions.mixed, assume_type=self.class_name)

        return [self.accessor_class_field, self.linked_accessor_types_field]

    def create_final(self) -> None:
        super().create_final()
        self.final = AccessorType.AccessorType(
            name=self.name,
            class_arguments=self.class_arguments,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        exceptions.extend(self.linked_accessor_types_field.check_coverage_types(lambda component: component.accessor_class_field.get_final(), self.accessor_class_field.get_final().linked_accessors, self))
        trace = TypeVerifier.Trace([(self.accessor_class_field.get_final(), TypeVerifier.TraceItemType.OTHER)])
        exceptions.extend(self.accessor_class_field.get_final().class_parameters.verify(self.class_arguments, trace))
        self.get_final().link_finals(
            accessor_class=self.accessor_class_field.get_final(),
            get_linked_accessor_types=dict(self.linked_accessor_types_field.map(lambda key, component: component.get_final()))
        )
        return exceptions
