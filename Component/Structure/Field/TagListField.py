from typing import Self, Sequence

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Component.Structure.StructureTagComponent as StructureTagComponent
import Structure.StructureTag as StructureTag


class TagListField(ComponentListField.ComponentListField["StructureTagComponent.StructureTagComponent"]):

    __slots__ = (
        "_finals",
        "import_from_field",
        "tag_sets",
    )

    def __init__(self, subcomponents_strs:Sequence[str]|str, path:tuple[str,...]) -> None:
        '''
        :subcomponents_strs: The names of the TagComponents this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_strs, StructureTagComponent.TAG_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_component_group="structure_tags")
        self.tag_sets:list[set["StructureTagComponent.StructureTagComponent"]] = []
        self.import_from_field:TagListField|None = None
        self._finals:set[StructureTag.StructureTag]|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[Sequence["StructureTagComponent.StructureTagComponent"],Sequence["StructureTagComponent.StructureTagComponent"]]:
        subcomponents, inline_components = super().set_field(source_component, components, global_components, functions, create_component_function)
        if self.import_from_field is not None:
            self.import_from_field.set_field(source_component, components, global_components, functions, create_component_function)
            self.extend(self.import_from_field.subcomponents)
        for tag_set in self.tag_sets:
            tag_set.update(self.subcomponents)
        return subcomponents, inline_components

    def import_from(self, tag_list_field:"TagListField") -> Self:
        '''
        Makes this TagListField import from another TagListField when `set_field` is called.
        :tag_list_field: The TagListField to import from.
        '''
        self.import_from_field = tag_list_field
        return self

    def add_to_tag_set(self, tag_set:set["StructureTagComponent.StructureTagComponent"]) -> Self:
        '''
        Makes this TagListField add its tags to the given tag set.
        :tag_set: The set of StructureTags to add to.
        '''
        self.tag_sets.append(tag_set)
        return self

    @property
    def finals(self) -> set[StructureTag.StructureTag]:
        '''
        Returns the `final` attribute of all tags in this TagListField.
        Can only be called after `set_field`.
        '''
        if self._finals is None:
            self._finals = {tag.final for tag in self.subcomponents}
        return self._finals
