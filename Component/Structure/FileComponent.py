import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Serializer.Field.SerializerField as SerializerField
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.StructureComponentField as StructureComponentField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.FileStructure as FileStructure
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class FileComponent(StructureComponent.StructureComponent[FileStructure.FileStructure]):

    class_name_article = "an NbtBase"
    class_name = "NbtBase"
    children_has_normalizer_default = True
    my_capabilities = Capabilities.Capabilities(is_file=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer", "a str or dict", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or StructureComponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.FileTypedDict, name: str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.subcomponent_field = StructureComponentField.StructureComponentField(data["subcomponent"], ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), ["delegate"])
        self.serializer_field = SerializerField.SerializerField(data["serializer"], ["serializer"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.types_field.verify_with(self.subcomponent_field)
        self.types_field.must_be(StructureComponent.NBT_TYPES)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.fields.extend([self.subcomponent_field, self.delegate_field, self.serializer_field, self.types_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = FileStructure.FileStructure(
            name = self.name,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        types = self.types_field.get_types()
        self.my_type = set(types)
        self.my_type.add(File.File)
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            delegate=self.delegate_field.create_delegate(self.get_final(), exceptions=exceptions),
            serializer=self.serializer_field.get_component().get_final(),
            types=types,
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else types,
        )
        return exceptions
