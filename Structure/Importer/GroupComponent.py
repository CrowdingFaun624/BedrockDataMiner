import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.FieldListField as FieldListField
import Structure.Importer.Field.GroupItemField as GroupItemField
import Structure.Importer.ImporterConfig as ImporterConfig
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
        assert self.final is not None
        for group_field in self.subcomponents_field:
            valid_types = group_field.get_types()
            subcomponent = group_field.get_component()
            self.my_type.update(valid_types)
            if subcomponent is None:
                structure = None
            else:
                structure = subcomponent.final
            for valid_type in valid_types:
                self.final[valid_type] = structure
