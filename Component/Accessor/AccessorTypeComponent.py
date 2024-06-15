import Component.Accessor.Field.AccessorClassField as AccessorClassField
import Component.Accessor.Field.ManagerClassField as ManagerClassField
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.TypeVerifierField as TypeVerifierField
import Downloader.AccessorType as AccessorType
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class AccessorTypeComponent(Component.Component[AccessorType.AccessorType]):

    class_name = "AccessorType"
    class_name_article = "an AccessorType"
    my_capabilities = Capabilities.Capabilities(is_accessor_type=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("accessor_class", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("manager_class", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("parameters", "a TypeVerifier", True, dict)
    )

    def __init__(self, data: ComponentTyping.AccessorTypeTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.accessor_class_field = AccessorClassField.AccessorClassField(data["accessor_class"], ["accessor_class"])
        self.manager_class_field = ManagerClassField.ManagerClassField(data["manager_class"], ["manager_class"])
        self.parameters_field = TypeVerifierField.TypeVerifierField(data["parameters"], ["parameters"])
        self.fields.extend([self.accessor_class_field, self.manager_class_field, self.parameters_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = AccessorType.AccessorType(
            name=self.name,
        )

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_finals(
            manager_class=self.manager_class_field.get_final(),
            accessor_class=self.accessor_class_field.get_final(),
            parameters=self.parameters_field.get_final()
        )
