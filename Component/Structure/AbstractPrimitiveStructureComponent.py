from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Structure.Field.DelegateField as DelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.PrimitiveStructure as PrimitiveStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class AbstractPrimitiveStructureComponent[a: PrimitiveStructure.PrimitiveStructure](StructureComponent.StructureComponent[a]):

    __slots__ = (
        "delegate_field",
        "normalizers_field",
        "pre_normalized_types_field",
        "tags_field",
        "this_types_field",
    )

    default_this_types_name:tuple[str,...] = () # default of `this_types` field.
    type_verifier = StructureComponent.StructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizers", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: ComponentTyping.PrimitiveStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate", "PrimitiveDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.normalizers_field = ComponentListField.ComponentListField(data.get("normalizers", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizers",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.tags_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.this_types_field = TypeListField.TypeListField(data.get("this_types", self.default_this_types_name), ("this_types",)).add_to_set(self.my_type)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",)).default_to(self.this_types_field)

        fields.extend((self.delegate_field, self.normalizers_field, self.pre_normalized_types_field, self.tags_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_primitive_structure(
                delegate=self.delegate_field.create_delegate(self.final, trace),
                normalizers=tuple(self.normalizers_field.map(lambda subcomponent: subcomponent.final)),
                pre_normalized_types=self.pre_normalized_types_field.types,
                tags=self.tags_field.finals,
                this_types=self.this_types_field.types,
            )
