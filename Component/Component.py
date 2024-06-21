from typing import (TYPE_CHECKING, Any, Callable, Generic, Mapping, Sequence,
                    TypeVar)

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Field.Field as Field

a = TypeVar("a")

class Component(Generic[a]):

    class_name_article = "a Component"
    class_name = "Component"
    my_capabilities:Capabilities.Capabilities
    children_has_normalizer_default = False
    type_verifier:TypeVerifier.TypeVerifier

    def __init__(self, data:Any, name:str, component_group:str, index:int|None) -> None:
        self.name = name
        self.component_group = component_group
        self.index = index
        self.links_to_other_components:list[Component] = []
        self.parents:list[Component] = []
        self.final:a|None = None
        self.children_has_normalizer = self.children_has_normalizer_default
        self.children_tags:set[str] = set()
        self.fields:list["Field.Field"] = []
        self.inline_components:list[Component]|None = None
        self.inline_component_count = 0
        self.inline_parent:Component|None = None

    def get_index(self) -> int:
        "Returns the index of this Component in the Component group. Raises an error if it doesn't have an index."
        if self.index is None:
            raise Exceptions.AttributeNoneError("index", self)
        return self.index

    def get_inline_parent(self) -> "Component":
        "Returns the parent of this Component if it is an inline Component. If it isn't, an error is raised."
        if self.inline_parent is None:
            raise Exceptions.AttributeNoneError("inline_parent", self)
        return self.inline_parent

    def get_inline_component_name(self) -> str:
        output = self.name + ".%i" % (self.inline_component_count)
        self.inline_component_count += 1
        return output

    def get_all_descendants(self, memo:set["Component"]) -> list["Component"]:
        '''
        Returns a list of the Component, its childern, its grandchildren, and so on.
        :memo: The set of all Components already added to the list, ensuring no duplicates or infinite loops.
        '''
        result:list[Component] = []
        if self not in memo:
            result.append(self)
            memo.add(self)
            for child in self.links_to_other_components:
                result.extend(child.get_all_descendants(memo))
        return result

    def get_final(self) -> a:
        if self.final is None:
            raise Exceptions.AttributeNoneError("final", self)
        return self.final

    def link_components(self, components:Sequence["Component"]) -> None:
        self.links_to_other_components.extend(components)
        for component in components:
            component.parents.append(self)

    def verify_arguments(self, data:Mapping[str,Any], name:str) -> None:
        self.type_verifier.base_verify(data, [repr(self)])

    def set_component(self, components:dict[str,"Component"], imported_components:dict[str,dict[str,"Component"]], functions:dict[str,Callable], create_component_function:ComponentTyping.CreateComponentFunction) -> None:
        '''Links this Component to other Components'''
        self.inline_components = []
        for field in self.fields:
            linked_components, new_inline_components = field.set_field(self, components, imported_components, functions, create_component_function)
            self.link_components(linked_components)
            self.inline_components.extend(new_inline_components)
        for inline_component in self.inline_components:
            inline_component.set_component(components, imported_components, functions, create_component_function)

    def create_final(self) -> None:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        for field in self.fields:
            field.resolve_create_finals()
        if self.inline_components is None:
            raise Exceptions.AttributeNoneError("inline_components", self)
        for inline_component in self.inline_components:
            inline_component.create_final()

    def link_finals(self) -> None:
        '''Links this Component's final object to other final objects.'''
        for field in self.fields:
            field.resolve_link_finals()
        if self.inline_components is None:
            raise Exceptions.AttributeNoneError("inline_components", self)
        for inline_component in self.inline_components:
            inline_component.link_finals()

    def check(self) -> list[Exception]:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        exceptions:list[Exception] = []
        for field in self.fields:
            exceptions.extend(field.check(self))
        if self.inline_components is None:
            raise Exceptions.AttributeNoneError("inline_components", self)
        for inline_component in self.inline_components:
            exceptions.extend(inline_component.check())
        return exceptions

    def finalize(self) -> None:
        '''Used to call on the structure once all structures and components are guaranteed to be linked.'''
        if self.inline_components is None:
            raise Exceptions.AttributeNoneError("inline_components", self)
        for inline_component in self.inline_components:
            inline_component.finalize()

    def propagate_variables(self) -> bool:
        has_changed = False
        for child in self.links_to_other_components:
            if child.children_has_normalizer and not self.children_has_normalizer:
                self.children_has_normalizer = True
                has_changed = True
            if self.children_tags is not None and child.children_tags is not None:
                tags_length_before = len(self.children_tags)
                self.children_tags.update(child.children_tags)
                has_changed = has_changed or len(self.children_tags) != tags_length_before
        return has_changed

    def __hash__(self) -> int:
        return hash((self.name, self.component_group))

    def __repr__(self) -> str:
        return "<%s %s in %s>" % (self.class_name, self.name, self.component_group)
