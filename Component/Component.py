from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Field.Field as Field
    import Component.Structure.StructureTagComponent as StructureTagComponent

class Component[a]():

    class_name_article = "a Component"
    class_name = "Component"
    my_capabilities:Capabilities.Capabilities
    children_has_normalizer_default = False
    type_verifier:TypeVerifier.TypeVerifier

    __slots__ = (
        "children_has_garbage_collection",
        "children_has_normalizer",
        "children_tags",
        "component_group",
        "domain",
        "fields",
        "final",
        "index",
        "inline_component_count",
        "inline_components",
        "inline_parent",
        "links_to_other_components",
        "name",
        "parents",
    )

    def __init__(self, data:Any, name:str, domain:"Domain.Domain", component_group:str, index:int|None) -> None:
        self.name = name
        self.domain = domain
        self.component_group = component_group
        self.index = index

        self.verify_arguments(data)

        self.links_to_other_components:list[Component] = []
        self.parents:list[Component] = []
        self.final:a
        self.children_has_normalizer = self.children_has_normalizer_default
        self.children_has_garbage_collection = False
        self.children_tags:set[StructureTagComponent.StructureTagComponent] = set()
        self.fields:list["Field.Field"] = []
        self.inline_components:list[Component]
        self.inline_component_count = 0
        self.inline_parent:Component|None = None

        self.fields.extend(self.initialize_fields(data))
        for field in self.fields:
            field.set_domain(self.domain)

    def initialize_fields(self, data:Any) -> list["Field.Field"]:
        return []

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
        output = self.name + f".{self.inline_component_count}"
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

    def link_components(self, components:Sequence["Component"]) -> None:
        self.links_to_other_components.extend(components)
        for component in components:
            component.parents.append(self)

    def verify_arguments(self, data:Mapping[str,Any]) -> None:
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

    def create_final_component(self) -> a:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        for field in self.fields:
            field.resolve_create_finals()
        for inline_component in self.inline_components:
            inline_component.final = inline_component.create_final_component()
        return self.create_final()

    def create_final(self) -> a:
        '''Method overridden by subclasses. Returns the Component's object.'''
        ...

    def link_finals(self) -> list[Exception]:
        '''Links this Component's final object to other final objects.'''
        exceptions:list[Exception] = []
        for field in self.fields:
            field.resolve_link_finals()
        for inline_component in self.inline_components:
            exceptions.extend(inline_component.link_finals())
        return exceptions

    def check(self) -> list[Exception]:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        exceptions:list[Exception] = []
        for field in self.fields:
            exceptions.extend(field.check(self))
        for inline_component in self.inline_components:
            exceptions.extend(inline_component.check())
        return exceptions

    def finalize(self) -> list[Exception]:
        '''Used to call on the structure once all structures and components are guaranteed to be linked.'''
        return list(chain.from_iterable(inline_component.finalize() for inline_component in self.inline_components))

    def propagate_variables(self) -> bool:
        has_changed = False
        for child in self.links_to_other_components:
            if child.children_has_normalizer and not self.children_has_normalizer:
                self.children_has_normalizer = True
                has_changed = True
            if child.children_has_garbage_collection and not self.children_has_garbage_collection:
                self.children_has_garbage_collection = True
                has_changed = True
                print(self)
            if self.children_tags is not None and child.children_tags is not None:
                tags_length_before = len(self.children_tags)
                self.children_tags.update(child.children_tags)
                has_changed = has_changed or len(self.children_tags) != tags_length_before
        return has_changed

    def __hash__(self) -> int:
        return hash((self.name, self.component_group))

    def __repr__(self) -> str:
        return f"<{self.class_name} {self.name} in {self.component_group}>"
