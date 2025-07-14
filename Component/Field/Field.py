import enum
from types import EllipsisType
from typing import TYPE_CHECKING, Callable, Iterable, Mapping, Sequence, cast

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.InheritedComponent import InheritedComponent
from Component.Pattern import AbstractPattern
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Component import Component
    from Component.Group import Group

def get_options(
    source_component:"Component",
    pattern:AbstractPattern,
    local_group:"Group",
    global_groups:Mapping[str,Mapping[str,"Group"]],
    other_options:Iterable[str]|None,
) -> list[str]:
    reversed_group_aliases:dict[str,dict[str, list[str]]] = {domain_name: {group_name: [group_name] for group_name in groups.keys()} for domain_name, groups in global_groups.items()}
    for alias, target in local_group.group_aliases.items():
        reversed_group_aliases[local_group.domain.name][target].append(alias)
    options:list[str] = []
    if other_options is not None:
        options.extend(other_options)
    options.extend(component_name for component_name, component in local_group.components.items() if pattern.contains(component))
    options.extend(
        f"{group_name_alias}/{component_name}"
        for group_name, group in global_groups[source_component.domain.name].items()
        for component_name, component in group.components.items()
        if pattern.contains(component)
        for group_name_alias in reversed_group_aliases[source_component.domain.name][group_name]
    )
    options.extend(
        f"{domain_name}!{group_name_alias}/{component_name}"
        for domain_name, domain_components in global_groups.items()
        for group_name, group in domain_components.items()
        for component_name, component in group.components.items()
        if pattern.contains(component)
        for group_name_alias in reversed_group_aliases[domain_name][group_name]
    )
    return options

class InlinePermissions(enum.Enum):
    "Use when creating a Field to specify if it's allowed to have inline Components."
    inline = 0
    "Inline Components are allowed."
    mixed = 1
    "Both inline and reference Components are allowed."
    reference = 2
    "Only reference Components are allowed."

def resolve_reference(component_data:str, local_group:"Group") -> str:
    '''
    Returns an unambiguous reference that directs to the same Component as it does at `source_component`.
    :component_data: The Component reference that is ambiguous depending on which Group it originates from.
    :local_group: The Group that the reference originates from.
    '''
    bang_index = component_data.find("!")
    slash_index = component_data.rfind("/", bang_index if bang_index != -1 else 0)
    if bang_index == -1 and slash_index == -1: # neither ! nor /
        return f"{local_group.domain.name}!{local_group.name}/{component_data}"
    elif bang_index == -1: # only /
        alias_group_name = component_data[:slash_index] # could be an alias
        group_name = local_group.group_aliases.get(alias_group_name, alias_group_name)
        component_name = component_data[slash_index+1:]
        return f"{local_group.domain.name}!{group_name}/{component_name}"
    else: # ! and /
        domain_name = component_data[:bang_index]
        component_path = component_data[bang_index+1:]
        if slash_index != "-1":
            alias_group_name = component_path[:slash_index-bang_index-1]
            group_name = local_group.group_aliases.get(alias_group_name, alias_group_name)
            component_name = component_path[slash_index-bang_index:]
            return f"{domain_name}!{group_name}/{component_name}"
        else:
            raise Exceptions.MalformedComponentReferenceError(component_data, [], "because it has a ! and no /")

def refer_to_component[a:"Component"](
        component:"Component",
        parent_component:"Component|None",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        pattern:AbstractPattern[a],
        trace:Trace,
        allow_inherited:bool,
        pattern_fail_error:Callable[[], Exceptions.InvalidComponentError],
    ) -> a|EllipsisType:
    '''
    Function for referring to a Component. Raises an error if the pattern does not match the Component.
    :component: The Component found through `component_data`. May be an InheritedComponent.
    :parent_component: The inline parent Component of `component`.
    :global_groups: Every Group from every Domain loaded.
    :pattern: The Pattern the Component must follow.
    :allow_inherited: If True, InheritedComponents may be returned instead of resolving them.
    :pattern_fail_error: The InvalidComponentError to raise if the Component does not match the Pattern.
    '''
    if allow_inherited:
        return cast(a, component)
    new_component = component.inheritance(set(), global_groups, parent_component.variables if parent_component is not None else {}, trace)
    if new_component is ...:
        return ... # error
    if not pattern.contains(new_component):
        trace.exception(pattern_fail_error())
        return ...
    if new_component.abstract: # meaning it has undefined Variables
        trace.exception(Exceptions.AbstractComponentError(new_component, new_component.variables.keys()))
        return ...
    return new_component

def choose_component[a: "Component"](
        component_data:str|ComponentTypedDicts,
        source_component:"Component",
        pattern:AbstractPattern[a],
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        trace:Trace,
        keys:tuple[str,...],
        create_component_function:CreateComponentFunction|None,
        assume_type:str|None,
        other_options:Iterable[str]|None=None,
        allow_inherited:bool=False
    ) -> tuple[a|EllipsisType,bool]:
    '''
    Finds a Component with the same name and properties if `component_data` is a str.
    If `component_data` is a dict, it creates a new inline Component using the `create_component_function`.

    :return: A tuple of the Component and if it is an inline Component
    :component_data: The Component name or dictionary of Component data.
    :source_component: The Component referring to the given subcomponent name or subcomponent.
    :pattern: The Pattern the Component must follow.
    :local_group: The Group that this Field originates from.
    :global_groups: Every Group from every Domain loaded.
    :keys: The path through the source Component to get to this Component.
    :create_component_function: The function used to create new inline Components.
    :assume_type: What to use as the type key of an inline Component if it is missing.
    :other_options: Additional values to supply to `get_options` in the event of an error.
    :allow_inherited: If True, InheritedComponents may be returned instead of resolving them.
    '''
    # inline Component
    if isinstance(component_data, dict):
        if create_component_function is None: # only happens in InheritedComponent.
            trace.exception(Exceptions.InlineComponentError(source_component, None, component_data))
            return ..., True
        component = create_component_function(component_data, source_component, assume_type, keys)
        if component is ...:
            return ..., True
        return refer_to_component(component, source_component, global_groups, pattern, trace, allow_inherited, lambda: Exceptions.InvalidComponentError(component, None, pattern, component.my_capabilities, None)), True

    # neither ! nor /
    bang_index = component_data.find("!")
    slash_index = component_data.rfind("/", bang_index if bang_index != -1 else 0)

    if bang_index == -1 and slash_index == -1:
        group = local_group
        if (component := group.components.get(component_data)) is None:
            options = get_options(source_component, pattern, local_group, global_groups, other_options)
            trace.exception(Exceptions.UnrecognizedComponentError(component_data, component_data, options))
            return ..., False
        return refer_to_component(component, None, global_groups, pattern, trace, allow_inherited, lambda: Exceptions.InvalidComponentError(
            component, component_data, pattern, component.my_capabilities, get_options(source_component, pattern, local_group, global_groups, other_options))), False

    # only /
    elif bang_index == -1:
        domain_components = global_groups[source_component.domain.name]
        alias_group_name = component_data[:slash_index] # could be an alias
        group_name = local_group.group_aliases.get(alias_group_name, alias_group_name)
        component_name = component_data[slash_index+1:]
        if (group := domain_components.get(group_name)) is None:
            options = get_options(source_component, pattern, local_group, global_groups, other_options)
            trace.exception(Exceptions.UnrecognizedGroupError(alias_group_name, component_data, options))
            return ..., False

    # ! and /
    else:
        domain_name = component_data[:bang_index]
        component_path = component_data[bang_index+1:]
        if (domain_components := global_groups.get(domain_name)) is None:
            options = get_options(source_component, pattern, local_group, global_groups, other_options)
            trace.exception(Exceptions.UnrecognizedComponentDomainError(domain_name, component_data, options))
            return ..., False
        if slash_index != -1:
            alias_group_name = component_path[:slash_index-bang_index-1]
            group_name = local_group.group_aliases.get(alias_group_name, alias_group_name)
            component_name = component_path[slash_index-bang_index:]
            if (group := domain_components.get(group_name)) is None:
                options = get_options(source_component, pattern, local_group, global_groups, other_options)
                trace.exception(Exceptions.UnrecognizedGroupError(alias_group_name, component_data, options))
                return ..., False
        else:
            options = get_options(source_component, pattern, local_group, global_groups, other_options)
            trace.exception(Exceptions.MalformedComponentReferenceError(component_data, options, "because it has a ! and no /"))
            return ..., False

    if (component := group.components.get(component_name)) is None:
        options = get_options(source_component, pattern, local_group, global_groups, other_options)
        trace.exception(Exceptions.UnrecognizedComponentError(component_name, component_data, options))
        return ..., False
    return refer_to_component(component, None, global_groups, pattern, trace, allow_inherited, lambda: Exceptions.InvalidComponentError(
        component, component_data, pattern, component.my_capabilities, get_options(source_component, pattern, local_group, global_groups, other_options))), False

class Field():
    '''Abstract class of Fields. Fields are a modular way to manage the data of Components.'''

    __slots__ = (
        "cumulative_path",
        "domain",
        "trace_path",
    )

    def __init__(self, path:tuple[str,...], cumulative_path:tuple[str,...]|None) -> None:
        '''
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        self.trace_path = path
        self.cumulative_path = path if cumulative_path is None else cumulative_path

    def set_domain(self, domain:"Domain.Domain") -> None:
        self.domain = domain

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        '''
        Links this Component to other Components. Returns a list of all children Components (including inline Components) as well as a list of all inline Components.
        Fields are not responsible for calling `set_component` on inline Components.
        :source_component: The Component that owns this Field.
        :local_group: A dictionary of all Components and with the keys as their names.
        :global_groups: A dictionary with keys of all DOmains and values of the the Group names and values.
        :functions: A dictionary of functions that is provided by the importer.
        :create_component_function: The function used to create inline Components.
        '''
        with trace.enter_keys(self.trace_path, ...):
            return (), ()
        return (), ()

    def resolve_link_finals(self, trace:Trace) -> None:
        '''
        Used for setting an attribute of this Field that requires a linked Component to have its final created.
        Ran during the link_finals stage.
        '''
        ...

    def check(self, source_component:"Component", trace:Trace) -> None:
        '''
        Make sure that this Component's types are all in order; no error could occur.
        :source_component: The Component that owns this Field.
        '''
        ...

    def finalize(self, trace:Trace) -> None:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)}>"
