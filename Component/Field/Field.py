import enum
from typing import Callable, Mapping

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions


def get_keys_strs(is_capital:bool, keys:list[str|int]) -> str:
    capitalize_function:Callable[[str,bool],str] = lambda string, capitalize: string.capitalize() if capitalize else string
    return "".join(
        capitalize_function(f"key \"{key}\" of " if isinstance(key, str) else f"item {key} of ", index == 0 and is_capital)
        for index, key in enumerate(reversed(keys))
    )
    
def get_source_str(keys:list[str|int], source_component:"Component.Component") -> str:
    return f"{get_keys_strs(False, keys)}{source_component}"

def get_options(
    source_component:"Component.Component",
    pattern:Pattern.Pattern,
    assume_component_group:str|None,
    local_components:Mapping[str,"Component.Component"],
    global_components:Mapping[str,Mapping[str,Mapping[str,"Component.Component"]]]
) -> list[str]:
    options:list[str] = []
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

def choose_component[a: Component.Component](
        component_data:str|ComponentTyping.ComponentTypedDicts,
        source_component:"Component.Component",
        pattern:Pattern.Pattern[a],
        local_components:Mapping[str,"Component.Component"],
        global_components:Mapping[str,Mapping[str,Mapping[str,"Component.Component"]]],
        keys:list[str|int],
        create_component_function:ComponentTyping.CreateComponentFunction,
        assume_type:str|None,
        assume_component_group:str|None,
    ) -> tuple[a,bool]:
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
        component = create_component_function(component_data, source_component, assume_type)
        if not pattern.contains(component):
            raise Exceptions.InvalidComponentError(component, None, get_source_str(keys, source_component), pattern, component.my_capabilities, None)
        return component, True

    # neither ! nor /
    elif all(((bang_index := component_data.find("!")) == -1, (slash_index := component_data.rfind("/", bang_index if bang_index != -1 else 0)) == -1)):
        if assume_component_group is None:
            components = local_components
        else:
            components = global_components[source_component.domain.name][assume_component_group]
        if (component := components.get(component_data)) is None:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
            raise Exceptions.UnrecognizedComponentError(component_data, component_data, get_source_str(keys, source_component), options)
        if not pattern.contains(component):
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
            raise Exceptions.InvalidComponentError(component, component_data, get_source_str(keys, source_component), pattern, component.my_capabilities, options)
        return component, False

    # only /
    elif bang_index == -1:
        domain_components = global_components[source_component.domain.name]
        component_group_name = component_data[:slash_index]
        component_name = component_data[slash_index+1:]
        if (component_group := domain_components.get(component_group_name)) is None:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
            raise Exceptions.UnrecognizedComponentGroupError(component_group_name, component_data, get_source_str(keys, source_component), options)

    # ! and perchance /
    else:
        domain_name = component_data[:bang_index]
        component_path = component_data[bang_index+1:]
        if (domain_components := global_components.get(domain_name)) is None:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
            raise Exceptions.UnrecognizedComponentDomainError(domain_name, component_data, get_source_str(keys, source_component), options)
        if slash_index != -1:
            component_group_name = component_path[:slash_index-bang_index]
            component_name = component_path[slash_index-bang_index+1:]
            if (component_group := domain_components.get(component_group_name)) is None:
                options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
                raise Exceptions.UnrecognizedComponentGroupError(component_group_name, component_data, get_source_str(keys, source_component), options)
        elif assume_component_group is not None:
            component_group = domain_components[assume_component_group]
            component_name = component_path
        else:
            options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
            raise Exceptions.MalformedComponentReferenceError(component_data, get_source_str(keys, source_component), options, "because it has a !, no /, and there is no assumed Component group")

    if (component := component_group.get(component_name)) is None:
        options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
        raise Exceptions.UnrecognizedComponentError(component_name, component_data, get_source_str(keys, source_component), options)
    if not pattern.contains(component):
        options = get_options(source_component, pattern, assume_component_group, local_components, global_components)
        raise Exceptions.InvalidComponentError(component, component_data, get_source_str(keys, source_component), pattern, component.my_capabilities, options)
    return component, False

class Field():
    '''Abstract class of Fields. Fields are a modular way to manage the data of Components.'''

    __slots__ = (
        "domain",
        "error_path",
    )

    def __init__(self, path:list[str|int]) -> None:
        '''
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        self.error_path = path

    def set_domain(self, domain:"Domain.Domain") -> None:
        self.domain = domain

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:"ScriptImporter.ScriptSetSetSet",
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        '''
        Links this Component to other Components. Returns a list of all children Components (including inline Components) as well as a list of all inline Components.
        Fields are not responsible for calling `set_component` on inline Components.
        :source_component: The Component that owns this Field.
        :components: A dictionary of all Components and with the keys as their names.
        :global_components: A dictionary with keys of the Component group and values of the imported components from that group.
        :functions: A dictionary of functions that is provided by the importer.
        :create_component_function: The function used to create inline Components.
        '''
        return [], []

    def resolve_create_finals(self) -> None:
        '''
        Used for setting an attribute of this Field that requires a linked Component to be set.
        Ran during the create_finals stage.
        '''
        ...

    def resolve_link_finals(self) -> None:
        '''
        Used for setting an attribute of this Field that requires a linked Component to have its final created.
        Ran during the link_finals stage.
        '''
        ...

    def check(self, source_component:"Component.Component") -> list[Exception]:
        '''
        Make sure that this Component's types are all in order; no error could occur.
        :source_component: The Component that owns this Field.
        '''
        return []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)}>"
