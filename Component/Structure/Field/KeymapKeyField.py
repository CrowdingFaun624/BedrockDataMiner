from typing import TYPE_CHECKING, Self

from Component.ComponentTyping import KeymapStructureKeyTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field, InlinePermissions
from Component.Field.FieldContainer import FieldContainer
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Component.Structure.StructureTagComponent import StructureTagComponent

if TYPE_CHECKING:
    from Component.Structure.KeymapStructureComponent import KeymapStructureComponent

class KeymapKeyField(FieldContainer[Field]):

    __slots__ = (
        "allow_inline",
        "delegate_arguments",
        "excluded_from_similarity",
        "key",
        "required",
        "similarity_weight",
        "source_component",
        "subcomponent_field",
        "tags_field",
        "tags_for_all_field",
        "types_field",
        "value_weight",
    )

    def __init__(
        self,
        data:KeymapStructureKeyTypedDict,
        key:str,
        tag_set:set["StructureTagComponent"],
        source_component:"KeymapStructureComponent",
        path:tuple[str,...],
        cumulative_path:tuple[str,...]|None=None,
        *,
        allow_inline:InlinePermissions=InlinePermissions.mixed,
    ) -> None:
        '''
        :data: A dictionary containing the keys data.
        :key: The key that this Field corresponds to.
        :tag_set: The set of tags to update when `set_field` is called.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :source_component: The original Component that owns this Field.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__([], path, cumulative_path)
        if cumulative_path is None: cumulative_path = path
        self.key = key
        self.source_component = source_component # used to make sure keys cannot be imported in chains.
        self.allow_inline = allow_inline
        self.delegate_arguments = data.get("delegate_arguments", {})
        self.required = data.get("required", False)
        self.similarity_weight = data.get("similarity_weight", 1)
        self.value_weight = data.get("weight", None)

        self.subcomponent_field = OptionalComponentField(data.get("structure", None), STRUCTURE_COMPONENT_PATTERN, ("structure",), (*cumulative_path, "structure"), allow_inline=allow_inline)
        self.tags_field = TagListField(data.get("tags", ()), ("tags",), (*cumulative_path, "tags")).add_to_tag_set(tag_set)
        self.types_field = TypeListField(data["types"] if isinstance(data["types"], list) else (data["types"]), ("types",), (*cumulative_path, "types")).verify_with(self.subcomponent_field)

        self.tags_for_all_field:TagListField|None = None

        self.fields.extend((self.types_field, self.subcomponent_field, self.tags_field))

    def add_tag_fields(self, tag_fields:TagListField) -> Self:
        '''
        Makes this KeymapKeyField extend its own tags_field when `set_field` is called.
        :tag_fields: The list of ComponentFields to add from.
        '''
        self.tags_field.import_from(tag_fields)
        return self

    def add_to_tag_set(self, tag_set:set["StructureTagComponent"]) -> None:
        '''
        Makes this KeymapKeyField add its tags (in string form) to the given tag set.
        :tag_set: The set of strings to add to.
        '''
        self.tags_field.add_to_tag_set(tag_set)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} id {id(self)}>"
