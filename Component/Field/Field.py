import enum
from types import EllipsisType
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.Pattern import Pattern
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

def get_options(
    source_component:"Component",
    pattern:Pattern,
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

def choose_component[a: Component](
        component_data:str|ComponentTypedDicts,
        source_component:"Component",
        pattern:Pattern[a],
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        trace:Trace,
        keys:tuple[str,...],
        create_component_function:CreateComponentFunction,
        assume_type:str|None,
        other_options:Iterable[str]|None=None,
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
    '''
    # inline Component
    if isinstance(component_data, dict):
        component = create_component_function(component_data, source_component, assume_type, keys)
        if component is ...:
            return ..., True
        if not pattern.contains(component):
            trace.exception(Exceptions.InvalidComponentError(component, None, pattern, component.my_capabilities, None))
            return ..., True
        return component, True

    # neither ! nor /
    elif all(((bang_index := component_data.find("!")) == -1, (slash_index := component_data.rfind("/", bang_index if bang_index != -1 else 0)) == -1)):
        group = local_group
        if (component := group.components.get(component_data)) is None:
            options = get_options(source_component, pattern, local_group, global_groups, other_options)
            trace.exception(Exceptions.UnrecognizedComponentError(component_data, component_data, options))
            return ..., False
        if not pattern.contains(component):
            options = get_options(source_component, pattern, local_group, global_groups, other_options)
            trace.exception(Exceptions.InvalidComponentError(component, component_data, pattern, component.my_capabilities, options))
            return ..., False
        return component, False

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
    if not pattern.contains(component):
        options = get_options(source_component, pattern, local_group, global_groups, other_options)
        trace.exception(Exceptions.InvalidComponentError(component, component_data, pattern, component.my_capabilities, options))
        return ..., False
    return component, False

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
        global_groups:dict[str,dict[str,"Group"]],
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

    def resolve_create_finals(self, trace:Trace) -> None:
        '''
        Used for setting an attribute of this Field that requires a linked Component to be set.
        Ran during the create_finals stage.
        '''
        ...

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
