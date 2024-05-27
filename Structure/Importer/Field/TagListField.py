from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.Field.ComponentListField as ComponentListField

if TYPE_CHECKING:
    import Structure.Importer.TagComponent as TagComponent

TAG_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_tag": True}])

class TagListField(ComponentListField.ComponentListField["TagComponent.TagComponent"]):

    def __init__(self, subcomponents_strs:list[str], path:list[str|int]) -> None:
        '''
        :subcomponents_strs: The names of the TagComponents this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_strs, TAG_REQUEST_PROPERTIES, path)
        self.tag_set:set[str]|None = None

    def set_field(self, component_name: str, component_class_name: str, components: dict[str, Component.Component], functions: dict[str, Callable]) -> Sequence[Component.Component]:
        output = super().set_field(component_name, component_class_name, components, functions)
        if self.tag_set is not None:
            self.tag_set.update(self.get_tags())
        return output

    def add_to_tag_set(self, tag_set:set[str]) -> None:
        '''
        Makes this TagListField add its tags (in string form) to the given tag set.
        :tag_set: The set of strings to add to.
        '''
        self.tag_set = tag_set

    def get_tags(self) -> list[str]:
        '''
        Returns the tags that this TagListField refers to in the form of strings.
        Can only be called after `set_field`.
        '''
        return [tag.name for tag in self.get_components()]
