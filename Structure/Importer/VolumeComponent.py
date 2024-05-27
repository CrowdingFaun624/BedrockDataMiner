from typing import cast

import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeField as TypeField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Normalizer as Normalizer
import Structure.VolumeStructure as VolumeStructure
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"has_keys": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])

class VolumeComponent(AbstractGroupComponent.AbstractGroupComponent):

    class_name_article = "a Volume"
    class_name = "Volume"
    my_type = {tuple}
    my_properties = ComponentCapabilities.Capabilities(is_group=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("position_key", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("print_additional_data", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("state_key", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def __init__(self, data:ComponentTyping.VolumeTypedDict, name: str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.field = data.get("field", "block")
        self.position_key = data["position_key"]
        self.print_additional_data = data.get("print_additional_data", True)
        self.state_key = data["state_key"]
        self.children_has_normalizer = True # has to turn into tuple that the thing recognizes.
        self.final:dict[type,VolumeStructure.VolumeStructure]|None=None
        self.final_structure:VolumeStructure.VolumeStructure|None=None
        self.my_type.add(tuple)

        self.subcomponent_field:OptionalComponentField.OptionalComponentField[StructureComponent.StructureComponent] = OptionalComponentField.OptionalComponentField(data.get("subcomponent"), COMPONENT_REQUEST_PROPERTIES, ["subcomponent"])
        self.normalizer_field:ComponentListField.ComponentListField[NormalizerComponent.NormalizerComponent] = ComponentListField.ComponentListField([] if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"]), NORMALIZER_REQUEST_PROPERTIES, ["normalizer"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.this_type_field = TypeField.TypeField(data["this_type"], ["this_type"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.fields.extend([self.subcomponent_field, self.normalizer_field, self.types_field, self.this_type_field, self.tags_field])

    def create_final(self) -> None:
        self.final_structure = VolumeStructure.VolumeStructure(
            name=self.name,
            field=self.field,
            position_key=self.position_key,
            state_key=self.state_key,
            structure=None,
            print_additional_data=self.print_additional_data,
            tags=list(self.tags_field.map(lambda tag_component: tag_component.name)),
            normalizer=[cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizer_field.get_components()],
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )
        self.final = {tuple: self.final_structure}
        for my_type in self.this_type_field.get_types(): self.final[my_type] = self.final_structure

    def link_finals(self) -> None:
        assert self.final_structure is not None
        subcomponent = self.subcomponent_field.get_component()
        if subcomponent is None:
            self.final_structure.structure = None
        else:
            self.final_structure.structure = subcomponent.final

    def check_components(self) -> list[Exception]:
        exceptions:list[Exception] = []
        subcomponent = self.subcomponent_field.get_component()
        component_types = self.types_field.get_types()
        if subcomponent is None:
            pass
        else:
            if set(component_types) != set(subcomponent.my_type):
                my_types = ", ".join(type_item.__name__ for type_item in component_types)
                its_types = ", ".join(type_item.__name__ for type_item in subcomponent.my_type)
                exceptions.append(TypeError("%s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, my_types, subcomponent.name, its_types)))
        return exceptions

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions:list[Exception] = []
        exceptions.extend(self.check_components())
        return exceptions
