import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.Pattern as Pattern
import Component.VersionTag.VersionTagComponent as VersionTagComponent

VERSION_TAG_PATTERN:Pattern.Pattern["VersionTagComponent.VersionTagComponent"] = Pattern.Pattern("is_version_tag")

class VersionTagOrderAllowedChildrenField(FieldContainer.FieldContainer[Field.Field]):

    __slots__ = (
        "children_field",
        "key_field",
    )

    def __init__(self, key:str, children:list[str], path: list[str | int]) -> None:
        '''
        :key: A key of the allowed_children dict.
        :children: The corresponding value of the key of the allowed_children dict.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        self.key_field = ComponentField.ComponentField(key, VERSION_TAG_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_component_group="version_tags")
        self.children_field = ComponentListField.ComponentListField(children, VERSION_TAG_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_component_group="version_tags")
        super().__init__([self.key_field, self.children_field], path)
