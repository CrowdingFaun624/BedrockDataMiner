from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence, Union

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.ImporterConfig as ImporterConfig
import Utilities.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Structure.Importer.Field.Field as Field

class Component():

    class_name_article = "a Component"
    class_name = "Component"

    my_properties:ComponentCapabilities.Capabilities
    children_has_normalizer_default = False
    type_verifier:TypeVerifier.TypeVerifier

    name: str
    fields:list["Field.Field"]
    links_to_other_components:list["Component"]
    parents:list["Component"]
    children_has_normalizer:bool
    children_tags:set[str]|None=None

    def __init__(self, data:ComponentTyping.ComponentTypedDicts, name:str) -> None: ...

    def link_components(self, components:Sequence["Component"]) -> None:
        self.links_to_other_components.extend(components)
        for component in components:
            component.parents.append(self)

    def verify_arguments(self, data:Mapping[str,Any], name:str) -> None:
        self.type_verifier.base_verify(data, ["%s \"%s\"" % (self.class_name, name)])

    def set_component(self, components:dict[str,"Component"], functions:dict[str,Callable]) -> None:
        '''Links this Component to other Components'''
        for field in self.fields:
            linked_components = field.set(self.name, self.class_name, components, functions)
            self.link_components(linked_components)

    def create_final(self) -> None:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        pass

    def link_finals(self) -> None:
        '''Links this Component's final object to other final objects.'''
        pass

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        exceptions:list[Exception] = []
        for field in self.fields:
            exceptions.extend(field.check(self.name, self.class_name, config))
        return exceptions

    def finalize_finals(self) -> None:
        '''Can be used to call a method on the final object.'''
        pass

    def propagate_variables(self, child:Union["Component",None]=None) -> None:
        '''Calls `propagates_variables` on the parents of this Component with the child.'''
        has_changed = False
        if child is not None:
            if child.children_has_normalizer and not self.children_has_normalizer:
                self.children_has_normalizer = True
                has_changed = True
            if self.children_tags is not None and child.children_tags is not None:
                tags_length_before = len(self.children_tags)
                self.children_tags.update(child.children_tags)
                has_changed = has_changed or len(self.children_tags) != tags_length_before
        if has_changed or child is None:
            for parent in self.parents:
                parent.propagate_variables(self)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<%s %s>" % (self.class_name, self.name)
