import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.FieldListField as FieldListField
import Component.Structure.AbstractGroupComponent as AbstractGroupComponent
import Component.Structure.Field.GroupItemField as GroupItemField
import Structure.Structure as Structure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GroupComponent(AbstractGroupComponent.AbstractGroupComponent[Structure.Structure]):

    class_name_article = "a Group"
    class_name = "Group"
    my_capabilities = Capabilities.Capabilities(is_group=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, (str, dict, type(None)), "a dict", "a str", "a str, StructureComponent, or None")),
    )

    def __init__(self, data:ComponentTyping.GroupComponentTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.subcomponents_field:FieldListField.FieldListField[GroupItemField.GroupItemField] = FieldListField.FieldListField([
            GroupItemField.GroupItemField(type_str, subcomponent_str, ["subcomponents", index])
            for index, (type_str, subcomponent_str) in enumerate(data["subcomponents"].items())], ["subcomponents"])
        self.fields.extend([self.subcomponents_field])

    def get_subcomponents(self) -> list[Component.Component]:
        return [group_item_component for group_item in self.subcomponents_field if (group_item_component := group_item.get_component()) is not None]

    def create_final(self) -> None:
        super().create_final()
        self.final = {}

    def link_finals(self) -> None:
        super().link_finals()
        final = self.get_final()
        for group_field in self.subcomponents_field:
            valid_types = group_field.get_types()
            self.my_type.update(valid_types)
            for valid_type in valid_types:
                final[valid_type] = group_field.subcomponent_field.get_final()