import re
from types import EllipsisType
from typing import Any, Mapping, Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

INVALID_NAME_REGEXP = re.compile(r"[\@\\\/\s\{\}\[\]\(\)\"\!]")

class Component[a]():

    class_name:str = "Component"
    my_capabilities:Capabilities.Capabilities
    type_verifier:TypeVerifier.TypedDictTypeVerifier
    script_referenceable:bool = False
    '''
    If the final of this Component may be accessed directly by Scripts.
    '''

    __slots__ = (
        "component_group",
        "domain",
        "fields",
        "final",
        "index",
        "inline_components",
        "inline_parent",
        "links_to_other_components",
        "name",
        "parents",
        "variable_bools",
        "variable_sets",
    )

    def __init__(self, data:Any, name:str, domain:"Domain.Domain", component_group:str, index:int|None, trace:Trace.Trace) -> None:
        self.name = name
        self.domain = domain
        self.component_group = component_group
        self.index = index
        if INVALID_NAME_REGEXP.match(name):
            trace.exception(Exceptions.ComponentInvalidNameError(self))
            return

        self.links_to_other_components:list[Component] = []
        self.parents:list[Component] = []
        self.final:a
        self.inline_components:list[Component]
        self.inline_parent:Component|None = None
        self.variable_bools, self.variable_sets = self.get_propagated_variables()

        self.fields:Sequence["Field.Field"] = self.initialize_fields(data)
        for field in self.fields:
            field.set_domain(self.domain)

    def initialize_fields(self, data:Any) -> Sequence["Field.Field"]:
        return ()

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

    def get_inline_component_name(self, path:tuple[str,...]) -> str:
        output = self.name + "".join(f"({item})" for item in path)
        return output

    def get_all_descendants(self, memo:set["Component"], trace:Trace.Trace) -> list["Component"]:
        '''
        Returns a list of the Component, its childern, its grandchildren, and so on.
        :memo: The set of all Components already added to the list, ensuring no duplicates or infinite loops.
        '''
        with trace.enter(self, self.name, ...):
            result:list[Component] = []
            if self not in memo:
                result.append(self)
                memo.add(self)
                for child in self.links_to_other_components:
                    result.extend(child.get_all_descendants(memo, trace))
            return result
        return []

    def link_components(self, components:Sequence["Component"]) -> None:
        self.links_to_other_components.extend(components)
        for component in components:
            component.parents.append(self)

    @classmethod
    def verify_arguments(cls, data:Mapping[str,Any], trace:Trace.Trace) -> bool:
        return cls.type_verifier.verify(data, trace)

    def set_component(
        self,
        components:dict[str,"Component"],
        global_components:dict[str,dict[str,dict[str,"Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
        trace:Trace.Trace,
    ) -> None:
        '''Links this Component to other Components'''
        with trace.enter(self, self.name, ...):
            self.inline_components = []
            for field in self.fields:
                linked_components, new_inline_components = field.set_field(self, components, global_components, functions, create_component_function, trace)
                self.link_components(linked_components)
                self.inline_components.extend(new_inline_components)
            for inline_component in self.inline_components:
                inline_component.set_component(components, global_components, functions, create_component_function, trace)

    def create_final_component(self, trace:Trace.Trace) -> a|EllipsisType:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.resolve_create_finals(trace)
            for inline_component in self.inline_components:
                inline_component.final = inline_component.create_final_component(trace)
            return self.create_final(trace)
        return ...

    def create_final(self, trace:Trace.Trace) -> a:
        '''
        Method overridden by subclasses. Returns the Component's object.

        You do not have to wrap this method in `with trace.enter` ....
        '''
        ...

    def link_finals(self, trace:Trace.Trace) -> None:
        '''Links this Component's final object to other final objects.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.resolve_link_finals(trace)
            for inline_component in self.inline_components:
                inline_component.link_finals(trace)

    def check(self, trace:Trace.Trace) -> None:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.check(self, trace)
            for inline_component in self.inline_components:
                inline_component.check(trace)

    def finalize(self, trace:Trace.Trace) -> None:
        '''Used to call on the structure once all structures and components are guaranteed to be linked.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.finalize(trace)
            for inline_component in self.inline_components:
                inline_component.finalize(trace)

    def get_propagated_variables(self) -> tuple[dict[str,bool], dict[str,set]]:
        return {}, {}

    def propagate_variables(self, trace:Trace.Trace) -> bool:
        with trace.enter(self, self.name, ...):
            has_changed = False
            # bools
            for variable_name, variable_value in self.variable_bools.items():
                with trace.enter_key(variable_name, variable_value):
                    for child in self.links_to_other_components:
                        other_value = child.variable_bools.get(variable_name)
                        if other_value is None:
                            continue
                        if other_value and not variable_value:
                            self.variable_bools[variable_name] = other_value
                            has_changed = True
            # sets
            for variable_name, variable_value in self.variable_sets.items():
                with trace.enter_key(variable_name, variable_value):
                    for child in self.links_to_other_components:
                        other_value = child.variable_sets.get(variable_name)
                        if other_value is None:
                            continue
                        length_before = len(variable_value)
                        variable_value.update(other_value)
                        has_changed = has_changed or len(variable_value) != length_before
            return has_changed
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.component_group, self.domain))

    @property
    def full_name(self) -> str:
        return f"{self.domain.name}!{self.component_group}/{self.name}"

    def __repr__(self) -> str:
        return f"<{self.class_name} {self.domain.name}!{self.component_group}/{self.name}>"
