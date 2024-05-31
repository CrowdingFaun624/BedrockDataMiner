import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.FieldListField as FieldListField
import Structure.Importer.Field.GroupItemField as GroupItemField
import Utilities.TypeVerifier as TypeVerifier


class GroupComponent(AbstractGroupComponent.AbstractGroupComponent):

    class_name_article = "a Group"
    class_name = "Group"
    my_properties = ComponentCapabilities.Capabilities(is_group=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, (str, type(None)), "a dict", "a str", "a str or None")),
    )

    def __init__(self, data:ComponentTyping.GroupComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.subcomponents_field:FieldListField.FieldListField[GroupItemField.GroupItemField] = FieldListField.FieldListField([
            GroupItemField.GroupItemField(type_str, subcomponent_str, ["subcomponents", index])
            for index, (type_str, subcomponent_str) in enumerate(data["subcomponents"].items())], ["subcomponents"])
        self.fields.extend([self.subcomponents_field])

    def create_final(self) -> None:
        self.final = {}

    def link_finals(self) -> None:
        super().link_finals()
        assert self.final is not None
        for group_field in self.subcomponents_field:
            valid_types = group_field.get_types()
            self.my_type.update(valid_types)
            for valid_type in valid_types:
                self.final[valid_type] = group_field.subcomponent_field.get_final()
