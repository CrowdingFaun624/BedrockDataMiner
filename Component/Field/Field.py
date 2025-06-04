import enum
from types import EllipsisType
from typing import Iterable, Mapping, Sequence

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.Pattern import Pattern
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace


def get_options(
    source_component:"Component",
    pattern:Pattern,
    assume_component_group:str|None,
    local_components:Mapping[str,"Component"],
    global_components:Mapping[str,Mapping[str,Mapping[str,"Component"]]],
    other_options:Iterable[str]|None,
) -> list[str]:
    options:list[str] = []
    if other_options is not None:
        options.extend(other_options)
    if assume_component_group is None:
        options.extend(component_name for component_name, component in local_components.items() if pattern.contains(component))
    else:
        options.extend(component_name for component_name, component in global_components[source_component.domain.name][assume_component_group].items() if pattern.contains(component))
        options.extend(
            f"{domain_name}!{component_name}"
            for domain_name, domain_components in global_components.items()
            for component_name, component in domain_components.get(assume_component_group, {}).items()
            if pattern.contains(component)
        )
    options.extend(
        f"{component_group_name}/{component_name}"
        for component_group_name, component_group in global_components[source_component.domain.name].items()
        for component_name, component in component_group.items()
        if pattern.contains(component)
    )
    options.extend(
        f"{domain_name}!{component_group_name}/{component_name}"
        for domain_name, domain_components in global_components.items()
        for component_group_name, component_group in domain_components.items()
        for component_name, component in component_group.items()
        if pattern.contains(component)
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
        local_components:Mapping[str,"Component"],
        global_components:Mapping[str,Mapping[str,Mapping[str,"Component"]]],
        trace:Trace,
        keys:tuple[str,...],
        create_component_function:CreateComponentFunction,
        assume_type:str|None,
        assume_component_group:str|None,
        other_options:Iterable[str]|None=None,
    ) -> tuple[a|EllipsisType,bool]:
    '''
    Finds a Component with the same name and properties if `component_data` is a str.
    If `component_data` is a dict, it creates a new inline Component using the `create_component_function`.

    :return: A tuple of the Component and if it is an inline Component
    :component_data: The Component name or dictionary of Component data.
    :source_component: The Component referring to the given subcomponent name or subcomponent.
    :pattern: The Pattern the Component must follow.
    :local_components: A dict of all Components in this Component group.
    :global_components: a dict of dicts of all Components from each Component Group.
    :keys: The path through the source Component to get to this Component.
    :create_component_function: The function used to create new inline Components.
    :assume_type: What to use as the type key of an inline Component if it is missing.
    :assume_component_group: Assumed Component group if it is not specified.
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
        if assume_component_group is None:
            components = local_components
        else:
            components = global_components[source_component.domain.name][assume_component_group]
        if (component := components.get(component_data)) is None:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
            trace.exception(Exceptions.UnrecognizedComponentError(component_data, component_data, options))
            return ..., False
        if not pattern.contains(component):
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
            trace.exception(Exceptions.InvalidComponentError(component, component_data, pattern, component.my_capabilities, options))
            return ..., False
        return component, False

    # only /
    elif bang_index == -1:
        domain_components = global_components[source_component.domain.name]
        component_group_name = component_data[:slash_index]
        component_name = component_data[slash_index+1:]
        if (component_group := domain_components.get(component_group_name)) is None:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
            trace.exception(Exceptions.UnrecognizedComponentGroupError(component_group_name, component_data, options))
            return ..., False

    # ! and perchance /
    else:
        domain_name = component_data[:bang_index]
        component_path = component_data[bang_index+1:]
        if (domain_components := global_components.get(domain_name)) is None:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
            trace.exception(Exceptions.UnrecognizedComponentDomainError(domain_name, component_data, options))
            return ..., False
        if slash_index != -1:
            component_group_name = component_path[:slash_index-bang_index]
            component_name = component_path[slash_index-bang_index+1:]
            if (component_group := domain_components.get(component_group_name)) is None:
                options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
                trace.exception(Exceptions.UnrecognizedComponentGroupError(component_group_name, component_data, options))
                return ..., False
        elif assume_component_group is not None:
            component_group = domain_components[assume_component_group]
            component_name = component_path
        else:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
            trace.exception(Exceptions.MalformedComponentReferenceError(component_data, options, "because it has a !, no /, and there is no assumed Component group"))
            return ..., False

    if (component := component_group.get(component_name)) is None:
        options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
        trace.exception(Exceptions.UnrecognizedComponentError(component_name, component_data, options))
        return ..., False
    if not pattern.contains(component):
        options = get_options(source_component, pattern, assume_component_group, local_components, global_components, other_options)
        trace.exception(Exceptions.InvalidComponentError(component, component_data, pattern, component.my_capabilities, options))
        return ..., False
    return component, False

class Field():
    '''Abstract class of Fields. Fields are a modular way to manage the data of Components.'''

    __slots__ = (
        "domain",
        "trace_path",
    )

    def __init__(self, path:tuple[str,...]) -> None:
        '''
        :path: The JSON keys that created this Field.
        '''
        self.trace_path = path

    def set_domain(self, domain:"Domain.Domain") -> None:
        self.domain = domain

    def set_field(
        self,
        source_component:"Component",
        components:dict[str,"Component"],
        global_components:dict[str,dict[str,dict[str,"Component"]]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        '''
        Links this Component to other Components. Returns a list of all children Components (including inline Components) as well as a list of all inline Components.
        Fields are not responsible for calling `set_component` on inline Components.
        :source_component: The Component that owns this Field.
        :components: A dictionary of all Components and with the keys as their names.
        :global_components: A dictionary with keys of the Component group and values of the imported components from that group.
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
