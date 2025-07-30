from typing import Sequence

from Component.ComponentTyping import PrimitiveStructureTypedDict
from Component.Field.Field import Field
from Component.Structure.Field.DelegateField import OptionalDelegateField
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.StructureComponent import StructureComponent
from Structure.PrimitiveStructure import PrimitiveStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class AbstractPrimitiveStructureComponent[a: PrimitiveStructure](StructureComponent[a]):

    __slots__ = (
        "delegate_field",
        "tags_field",
        "this_types_field",
    )

    default_this_types_name:tuple[str,...] = () # default of `this_types` field.
    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("this_types", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: PrimitiveStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.delegate_field = OptionalDelegateField(data.get("delegate", "PrimitiveDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.tags_field = TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.this_types_field = TypeListField(data.get("this_types", self.default_this_types_name), ("this_types",)).add_to_set(self.my_type)

        fields.extend((self.delegate_field, self.tags_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_primitive_structure(
            delegate=self.delegate_field.create_delegate(self.final, trace),
            tags=self.tags_field.finals,
            this_types=self.this_types_field.types,
        )
