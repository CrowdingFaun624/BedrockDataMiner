from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.Component as Component
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Pattern as Capabilities

if TYPE_CHECKING:
    import Structure.Importer.TagComponent as TagComponent

TAG_REQUEST_PROPERTIES:Capabilities.Pattern["TagComponent.TagComponent"] = Capabilities.Pattern([{"is_tag": True}])

class TagListField(ComponentListField.ComponentListField["TagComponent.TagComponent"]):

    def __init__(self, subcomponents_strs:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: The names of the TagComponents this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_strs, TAG_REQUEST_PROPERTIES, path)
        self.tag_sets:list[set[str]] = []
        self.import_from_field:TagListField|None = None

    def set_field(self, component_name: str, component_class_name: str, components: dict[str, Component.Component], functions: dict[str, Callable]) -> Sequence[Component.Component]:
        output = super().set_field(component_name, component_class_name, components, functions)
        if self.import_from_field is not None:
            self.import_from_field.set_field(component_name, component_class_name, components, functions)
            self.extend(self.import_from_field.get_components())
        for tag_set in self.tag_sets:
            tag_set.update(self.get_tags())
        return output

    def import_from(self, tag_list_field:"TagListField") -> None:
        '''
        Makes this TagListField import from another TagListField when `set_field` is called.
        :tag_list_field: The TagListField to import from.
        '''
        self.import_from_field = tag_list_field

    def add_to_tag_set(self, tag_set:set[str]) -> None:
        '''
        Makes this TagListField add its tags (in string form) to the given tag set.
        :tag_set: The set of strings to add to.
        '''
        self.tag_sets.append(tag_set)

    def get_tags(self) -> list[str]:
        '''
        Returns the tags that this TagListField refers to in the form of strings.
        Can only be called after `set_field`.
        '''
        return [tag.name for tag in self.get_components()]

    def get_finals(self) -> list[str]:
        '''
        Returns the `final` attribute of all tags in this TagListField.
        Can only be called after `set_field`.
        '''
        output:list[str] = []
        for tag in self.get_components():
            assert tag.final is not None
            output.append(tag.final)
        return output
