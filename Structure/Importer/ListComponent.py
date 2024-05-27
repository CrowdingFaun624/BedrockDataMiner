from typing import cast

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.ListStructure as ListStructure
import Structure.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])

class ListComponent(StructureComponent.StructureComponent):

    class_name_article = "a List"
    class_name = "List"
    my_type = [list]
    my_properties = ComponentCapabilities.Capabilities(is_structure=True)
    final:ListStructure.ListStructure
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("ordered", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def __init__(self, data:ComponentTyping.ListComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.field = data.get("field", "item")
        self.measure_length = data.get("measure_length", False)
        self.ordered = data.get("ordered", True)
        self.print_all = data.get("print_all", False)
        self.print_flat = data.get("print_flat", False)

        self.subcomponent_field:OptionalComponentField.OptionalComponentField[StructureComponent.StructureComponent|GroupComponent.GroupComponent] = OptionalComponentField.OptionalComponentField(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, ["subcomponent"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field:ComponentListField.ComponentListField[NormalizerComponent.NormalizerComponent] = ComponentListField.ComponentListField([] if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"]), NORMALIZER_REQUEST_PROPERTIES, ["normalizer"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.fields.extend([self.subcomponent_field, self.types_field, self.normalizer_field, self.tags_field])

    def create_final(self) -> None:
        self.final = ListStructure.ListStructure(
            name=self.name,
            field=self.field,
            structure=None,
            types=tuple(self.types_field.get_types()),
            print_flat=self.print_flat,
            print_all=self.print_all,
            measure_length=self.measure_length,
            normalizer=[cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizer_field.get_components()],
            ordered=self.ordered,
            tags=list(self.tags_field.map(lambda tag_component: tag_component.name)),
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        assert self.final is not None
        subcomponent = self.subcomponent_field.get_component()
        if subcomponent is None:
            self.final.structure = None
        else:
            self.final.structure = subcomponent.final
