from typing import TYPE_CHECKING, Callable, Iterable, Optional, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Version.VersionComponent as VersionComponent
    import Component.VersionTag.VersionTagComponent as VersionTagComponent

VERSION_TAG_PATTERN:Pattern.Pattern["VersionTagComponent.VersionTagComponent"] = Pattern.Pattern([{"is_version_tag": True}])

class VersionTagListField(ComponentListField.ComponentListField["VersionTagComponent.VersionTagComponent"]):

    def __init__(self, subcomponents_data:list[str]|str, path: list[str | int], version_component:Optional["VersionComponent.VersionComponent"]=None) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :version_component: The parent VersionComponent of this Field. If not given, will not auto-assign VersionTags to this Field.
        '''
        super().__init__(subcomponents_data, VERSION_TAG_PATTERN, path, allow_inline=Field.InlinePermissions.reference)
        self.version_component = version_component
        self.version_tag_components:Iterable["VersionTagComponent.VersionTagComponent"]|None = None

    def auto_assign(self, version_tag_components:Iterable["VersionTagComponent.VersionTagComponent"], version_component:"VersionComponent.VersionComponent") -> None:
        '''
        Adds auto-assigning VersionTags to this VersionTagListField.
        :version_component: The VersionComponent to test for inclusion.
        '''
        already_names = {linked_component.name for linked_component in self.get_components()}
        for version_tag_component in version_tag_components:
            if version_tag_component.name in already_names:
                continue
            for auto_assigner_component in version_tag_component.auto_assigner_field.get_components():
                if auto_assigner_component.contains_version(version_component):
                    cast(list["VersionTagComponent.VersionTagComponent"], self.subcomponents).append(version_tag_component)

    def resolve_create_finals(self) -> None:
        if self.version_tag_components is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.resolve_create_finals, self)
        if self.version_component is not None:
            self.auto_assign(self.version_tag_components, self.version_component)

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["VersionTagComponent.VersionTagComponent"],list["VersionTagComponent.VersionTagComponent"]]:
        linked_components, inline_components = super().set_field(source_component, components, imported_components, functions, create_component_function)
        self.version_tag_components = cast(dict[str,"VersionTagComponent.VersionTagComponent"], imported_components["version_tags"]).values()
        return linked_components, inline_components
