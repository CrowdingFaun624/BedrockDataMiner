from typing import Any, Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FunctionField as FunctionField
import Component.Structure.Field.DelegateField as DelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.IterableStructure as IterableStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class IterableStructureComponent[a: IterableStructure.IterableStructure](StructureComponent.StructureComponent[a]):

    __slots__ = (
        "delegate_field",
        "delegate_keys",
        "key_function_field",
        "key_types_field",
        "normalizers_field",
        "post_normalizers_field",
        "pre_normalized_types_field",
        "required_keys",
        "tags_field",
        "this_types_field",
    )

    default_this_types_name:str # default of `this_types` field.
    default_key_types_name:str # default of `key_types` field.
    type_verifier = StructureComponent.StructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("key_function", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("key_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizers", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizers", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("required_keys", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: ComponentTyping.IterableStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.required_keys:Sequence[str] = data.get("required_keys", ())
        self.delegate_keys:dict[str,Any]|None = None

        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.key_function_field = FunctionField.FunctionField(data.get("key_function", "identity"), ("key_function",))
        self.key_types_field = TypeListField.TypeListField(data.get("key_types", self.default_key_types_name), ("key_types",))
        self.normalizers_field = ComponentListField.ComponentListField(data.get("normalizers", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizers",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizers_field = ComponentListField.ComponentListField(data.get("post_normalizers", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizers",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.tags_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.this_types_field = TypeListField.TypeListField(data.get("this_types", self.default_this_types_name), ("this_types",)).add_to_set(self.my_type)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",)).default_to(self.this_types_field)
        fields.extend((self.delegate_field, self.key_function_field, self.key_types_field, self.normalizers_field, self.post_normalizers_field, self.pre_normalized_types_field, self.tags_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_iterable_structure(
                delegate=self.delegate_field.create_delegate(self.final, trace, self.delegate_keys),
                key_function=self.key_function_field.function,
                key_types=self.key_types_field.types,
                normalizers=tuple(self.normalizers_field.map(lambda subcomponent: subcomponent.final)),
                post_normalizers=tuple(self.post_normalizers_field.map(lambda subcomponent: subcomponent.final)),
                pre_normalized_types=self.pre_normalized_types_field.types,
                required_keys=set(self.required_keys),
                tags=self.tags_field.finals,
                this_types=self.this_types_field.types,
            )
