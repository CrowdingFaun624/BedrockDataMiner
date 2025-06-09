from types import EllipsisType
from typing import TYPE_CHECKING, Any, Mapping, Sequence

import Domain.Domain as Domain
from Utilities.Exceptions import (
    AttributeNoneError,
    ComponentInvalidNameCharacterError,
    ComponentInvalidNameError,
)
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Capabilities import Capabilities
    from Component.ComponentTyping import CreateComponentFunction
    from Component.Field.Field import Field
    from Component.ScriptImporter import ScriptSetSetSet
    from Utilities.TypeVerifier import TypedDictTypeVerifier

INVALID_NAME_CHARS = set("@\\/ \t\r\n\f\v{}[]()\"!")
INVALID_NAME_CHARS_DISPLAY = list("@\\/{}[]()\"!")
INVALID_NAMES:set[str] = {"*", "type", "inherit", "^"}

INVALID_NAME_CHARS_FILE = set("<>:\"\\/|?*")
INVALID_NAMES_FILE:set[str] = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(0, 10)} | {f"LPT{i}" for i in range(0, 10)}

class Component[a]():

    class_name:str = "Component"
    my_capabilities:"Capabilities"
    type_verifier:"TypedDictTypeVerifier"
    script_referenceable:bool = False
    restrict_to_file_names:bool = False
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

    def __init__(self, data:Any, name:str, domain:"Domain.Domain", component_group:str, index:int|None, trace:Trace) -> None:
        self.name = name
        self.domain = domain
        self.component_group = component_group
        self.index = index

        self.links_to_other_components:list[Component] = []
        self.parents:list[Component] = []
        self.final:a
        self.inline_components:list[Component]
        self.inline_parent:Component|None = None
        self.variable_bools, self.variable_sets = self.get_propagated_variables()

        name_exception:bool = False
        if index is not None and any(char in INVALID_NAME_CHARS for char in name):
            trace.exception(ComponentInvalidNameCharacterError(self, INVALID_NAME_CHARS_DISPLAY, "and whitespace characters"))
            name_exception = True
        elif index is not None and name in INVALID_NAMES:
            trace.exception(ComponentInvalidNameError(self, sorted(INVALID_NAMES)))
            name_exception = True
        elif index is not None and self.restrict_to_file_names and any(char in INVALID_NAME_CHARS_FILE for char in name):
            trace.exception(ComponentInvalidNameCharacterError(self, list(INVALID_NAME_CHARS_FILE), "(must be a valid file name)"))
            name_exception = True
        elif index is not None and self.restrict_to_file_names and name.upper() in INVALID_NAMES_FILE:
            trace.exception(ComponentInvalidNameError(self, sorted(INVALID_NAMES_FILE), "(must be a valid file name; case insensitive)"))
            name_exception = True
        if name_exception:
            self.fields = ()
            return

        self.fields:Sequence["Field"] = self.initialize_fields(data)
        for field in self.fields:
            field.set_domain(self.domain)

    def initialize_fields(self, data:Any) -> Sequence["Field"]:
        return ()

    def get_index(self) -> int:
        "Returns the index of this Component in the Component group. Raises an error if it doesn't have an index."
        if self.index is None:
            raise AttributeNoneError("index", self)
        return self.index

    def get_inline_parent(self) -> "Component":
        "Returns the parent of this Component if it is an inline Component. If it isn't, an error is raised."
        if self.inline_parent is None:
            raise AttributeNoneError("inline_parent", self)
        return self.inline_parent

    def get_inline_component_name(self, path:tuple[str,...]) -> str:
        output = self.name + "".join(f"({item})" for item in path)
        return output

    def get_all_descendants(self, memo:set["Component"], trace:Trace) -> list["Component"]:
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
    def verify_arguments(cls, data:Mapping[str,Any], trace:Trace) -> bool:
        return cls.type_verifier.verify(data, trace)

    def set_component(
        self,
        components:dict[str,"Component"],
        global_components:dict[str,dict[str,dict[str,"Component"]]],
        functions:"ScriptSetSetSet",
        create_component_function:"CreateComponentFunction",
        trace:Trace,
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

    def create_final_component(self, trace:Trace) -> a|EllipsisType:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.resolve_create_finals(trace)
            for inline_component in self.inline_components:
                inline_component.final = inline_component.create_final_component(trace)
            return self.create_final(trace)
        return ...

    def create_final(self, trace:Trace) -> a:
        '''
        Method overridden by subclasses. Returns the Component's object.

        You do not have to wrap this method in `with trace.enter` ....
        '''
        ...

    def link_finals(self, trace:Trace) -> None:
        '''Links this Component's final object to other final objects.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.resolve_link_finals(trace)
            for inline_component in self.inline_components:
                inline_component.link_finals(trace)

    def check(self, trace:Trace) -> None:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.check(self, trace)
            for inline_component in self.inline_components:
                inline_component.check(trace)

    def finalize(self, trace:Trace) -> None:
        '''Used to call on the structure once all structures and components are guaranteed to be linked.'''
        with trace.enter(self, self.name, ...):
            for field in self.fields:
                field.finalize(trace)
            for inline_component in self.inline_components:
                inline_component.finalize(trace)

    def get_propagated_variables(self) -> tuple[dict[str,bool], dict[str,set]]:
        return {}, {}

    def propagate_variables(self, trace:Trace) -> bool:
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
