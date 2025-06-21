from typing import TYPE_CHECKING, Self, Sequence

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import InlinePermissions
from Component.ScriptImporter import ScriptSetSetSet
from Component.Structure.StructureTagComponent import TAG_PATTERN, StructureTagComponent
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class TagListField(ComponentListField["StructureTagComponent"]):

    __slots__ = (
        "_finals",
        "import_from_field",
        "tag_sets",
    )

    def __init__(self, subcomponents_strs:Sequence[str]|str, path:tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponents_strs: The names of the TagComponents this Field refers to.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__(subcomponents_strs, TAG_PATTERN, path, cumulative_path, allow_inline=InlinePermissions.reference)
        self.tag_sets:list[set["StructureTagComponent"]] = []
        self.import_from_field:TagListField|None = None
        self._finals:set[StructureTag]|None = None

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:dict[str,dict[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["StructureTagComponent"],Sequence["StructureTagComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            subcomponents, inline_components = super().set_field(source_component, local_group, global_groups, functions, create_component_function, trace)
            if self.import_from_field is not None:
                self.import_from_field.set_field(source_component, local_group, global_groups, functions, create_component_function, trace)
                self.extend(self.import_from_field.subcomponents)
            for tag_set in self.tag_sets:
                tag_set.update(self.subcomponents)
            return subcomponents, inline_components
        return (), ()

    def import_from(self, tag_list_field:"TagListField") -> Self:
        '''
        Makes this TagListField import from another TagListField when `set_field` is called.
        :tag_list_field: The TagListField to import from.
        '''
        self.import_from_field = tag_list_field
        return self

    def add_to_tag_set(self, tag_set:set["StructureTagComponent"]) -> Self:
        '''
        Makes this TagListField add its tags to the given tag set.
        :tag_set: The set of StructureTags to add to.
        '''
        self.tag_sets.append(tag_set)
        return self

    @property
    def finals(self) -> set[StructureTag]:
        '''
        Returns the `final` attribute of all tags in this TagListField.
        Can only be called after `set_field`.
        '''
        if self._finals is None:
            self._finals = {tag.final for tag in self.subcomponents}
        return self._finals
