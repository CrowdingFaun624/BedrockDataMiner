from typing import TYPE_CHECKING, Iterable, Optional, Sequence, cast

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import InlinePermissions
from Component.ScriptImporter import ScriptSetSetSet
from Component.VersionTag.VersionTagComponent import (
    VERSION_TAG_PATTERN,
    VersionTagComponent,
)
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Version.VersionComponent import VersionComponent

class VersionTagListField(ComponentListField["VersionTagComponent"]):

    __slots__ = (
        "version_component",
        "version_tag_components",
    )

    def __init__(self, subcomponents_data:list[str]|str, path: tuple[str,...], version_component:Optional["VersionComponent"]=None) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :version_component: The parent VersionComponent of this Field. If not given, will not auto-assign VersionTags to this Field.
        '''
        super().__init__(subcomponents_data, VERSION_TAG_PATTERN, path, allow_inline=InlinePermissions.reference, assume_component_group="version_tags")
        self.version_component = version_component
        self.version_tag_components:Iterable["VersionTagComponent"]

    def auto_assign(self, version_tag_components:Iterable["VersionTagComponent"], version_component:"VersionComponent") -> None:
        '''
        Adds auto-assigning VersionTags to this VersionTagListField.
        :version_component: The VersionComponent to test for inclusion.
        '''
        already_names = {linked_component.name for linked_component in self.subcomponents}
        self.subcomponents.extend(
            version_tag_component
            for version_tag_component in version_tag_components
            if version_tag_component.name not in already_names
            if any(
                auto_assigner_component.contains_version(version_component)
                for auto_assigner_component in version_tag_component.auto_assigner_field.subcomponents
            )
        )

    def resolve_create_finals(self, trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            if self.version_component is not None:
                self.auto_assign(self.version_tag_components, self.version_component)

    def set_field(
        self,
        source_component:"Component",
        components:dict[str,"Component"],
        global_components:dict[str,dict[str,dict[str,"Component"]]],
        functions:ScriptSetSetSet,
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["VersionTagComponent"],Sequence["VersionTagComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            linked_components, inline_components = super().set_field(source_component, components, global_components, functions, create_component_function, trace)
            self.version_tag_components = cast(dict[str,"VersionTagComponent"], global_components[self.domain.name]["version_tags"]).values()
            return linked_components, inline_components
        return (), ()
