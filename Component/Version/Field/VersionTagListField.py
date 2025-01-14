from typing import Iterable, Optional, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Component.Version.VersionComponent as VersionComponent
import Component.VersionTag.VersionTagComponent as VersionTagComponent

VERSION_TAG_PATTERN:Pattern.Pattern["VersionTagComponent.VersionTagComponent"] = Pattern.Pattern("is_version_tag")

class VersionTagListField(ComponentListField.ComponentListField["VersionTagComponent.VersionTagComponent"]):

    __slots__ = (
        "version_component",
        "version_tag_components",
    )

    def __init__(self, subcomponents_data:list[str]|str, path: list[str | int], version_component:Optional["VersionComponent.VersionComponent"]=None) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :version_component: The parent VersionComponent of this Field. If not given, will not auto-assign VersionTags to this Field.
        '''
        super().__init__(subcomponents_data, VERSION_TAG_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_component_group="version_tags")
        self.version_component = version_component
        self.version_tag_components:Iterable["VersionTagComponent.VersionTagComponent"]

    def auto_assign(self, version_tag_components:Iterable["VersionTagComponent.VersionTagComponent"], version_component:"VersionComponent.VersionComponent") -> None:
        '''
        Adds auto-assigning VersionTags to this VersionTagListField.
        :version_component: The VersionComponent to test for inclusion.
        '''
        already_names = {linked_component.name for linked_component in self.subcomponents}
        subcomponents = cast(list["VersionTagComponent.VersionTagComponent"], self.subcomponents)
        subcomponents.extend(
            version_tag_component
            for version_tag_component in version_tag_components
            if version_tag_component.name not in already_names
            if any(
                auto_assigner_component.contains_version(version_component)
                for auto_assigner_component in version_tag_component.auto_assigner_field.subcomponents
            )
        )

    def resolve_create_finals(self) -> None:
        if self.version_component is not None:
            self.auto_assign(self.version_tag_components, self.version_component)

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["VersionTagComponent.VersionTagComponent"],list["VersionTagComponent.VersionTagComponent"]]:
        linked_components, inline_components = super().set_field(source_component, components, global_components, functions, create_component_function)
        self.version_tag_components = cast(dict[str,"VersionTagComponent.VersionTagComponent"], global_components[self.domain.name]["version_tags"]).values()
        return linked_components, inline_components
