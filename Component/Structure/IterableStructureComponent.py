from typing import Any, Sequence

from Component.ComponentTyping import IterableStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.DelegateField import OptionalDelegateField
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.FunctionComponent import FUNCTION_PATTERN
from Component.Structure.StructureComponent import StructureComponent
from Structure.IterableStructure import IterableStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class IterableStructureComponent[a: IterableStructure](StructureComponent[a]):

    __slots__ = (
        "delegate_field",
        "delegate_keys",
        "key_function_field",
        "key_types_field",
        "required_keys",
        "tags_field",
        "this_types_field",
    )

    default_this_types_name:str # default of `this_types` field.
    default_key_types_name:str # default of `key_types` field.
    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypedDictKeyTypeVerifier("key_function", False, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("key_types", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("required_keys", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("this_types", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: IterableStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.required_keys:Sequence[str] = data.get("required_keys", ())
        self.delegate_keys:dict[str,Any]|None = None

        self.delegate_field = OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.key_function_field = OptionalComponentField(data.get("key_function"), FUNCTION_PATTERN, ("key_function",), assume_type="Function")
        self.key_types_field = TypeListField(data.get("key_types", self.default_key_types_name), ("key_types",))
        self.tags_field = TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.this_types_field = TypeListField(data.get("this_types", self.default_this_types_name), ("this_types",)).add_to_set(self.my_type)
        fields.extend((self.delegate_field, self.key_function_field, self.key_types_field, self.tags_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        key_function = self.key_function_field.map(lambda subcomponent: subcomponent.final)
        if key_function is None: key_function = lambda data: data
        self.final.link_iterable_structure(
            delegate=self.delegate_field.create_delegate(self.final, trace, self.delegate_keys),
            key_function=key_function,
            key_types=self.key_types_field.types,
            required_keys=set(self.required_keys),
            tags=self.tags_field.finals,
            this_types=self.this_types_field.types,
        )
