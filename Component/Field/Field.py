import enum
from typing import Callable, Mapping, TypeVar, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions


def get_keys_strs(is_capital:bool, keys:list[str|int]) -> str:
    return "".join(
        ("%sey \"%s\" of " % ("K" if index == 0 and is_capital else "k", key)) if isinstance(key, str)
        else ("%stem %i of " % ("I" if index == 0 and is_capital else "i", key))
        for index, key in enumerate(reversed(keys))
    )

a = TypeVar("a")

class InLinePermissions(enum.Enum):
    "Use when creating a Field to specify if it's allowed to have inline Components."
    inline = 0
    "In-line Components are allowed."
    mixed = 1
    "Both inline and reference Components are allowed."
    reference = 2
    "Only reference Components are allowed."

def choose_component(
        component_data:str|ComponentTyping.ComponentTypedDicts|None,
        source_component:Component.Component,
        required_properties:Pattern.Pattern[a],
        components:Mapping[str,"Component.Component"],
        imported_components:Mapping[str,Mapping[str,"Component.Component"]],
        keys:list[str|int],
        create_component_function:ComponentTyping.CreateComponentFunction,
        assume_type:str|None,
    ) -> tuple[a,bool]:
    '''
    Finds a Component with the same name and properties if `component_data` is a str.
    If `component_data` is a dict, it creates a new inline Component using the `create_component_function`.
    If `component_data` is None, it will select the first Component that matches the `required_properties` Pattern; `imported_components` is ignored.
    Returns the Component and a bool specifying if the Component is inline.
    :component_data: The Component name or dictionary of Component data.
    :source_component: The Component referring to the given subcomponent name or subcomponent.
    :required_properties: The Pattern the Component must follow.
    :components: A dict of all Components in this Component group.
    :imported_components: a dict of dicts of all Components from each Component Group.
    :keys: The path through the source Component to get to this Component.
    :create_component_function: The function used to create new inline Components.
    :assume_type: What to use as the type key of an inline Component if it is missing.
    '''
    if component_data is None:
        is_inline = False
        for component in components.values():
            if component.my_capabilities in required_properties:
                break
        else:
            raise Exceptions.NoComponentMatchError(required_properties)
    elif isinstance(component_data, str):
        is_inline = False
        component = components.get(component_data, None)
        if component is None:
            for library in imported_components.values():
                component = library.get(component_data, None)
                if component is not None:
                    break
        if component is None:
            raise Exceptions.UnrecognizedComponentError(component_data, "%s%r" % (get_keys_strs(False, keys), source_component), "(should have %r)" % (required_properties,))
    else:
        is_inline = True
        component = create_component_function(component_data, source_component, assume_type)
    if component.my_capabilities not in required_properties:
        raise Exceptions.InvalidComponentError(component, source_component, required_properties, component.my_capabilities)
    return cast(a, component), is_inline

class Field():
    '''Abstract class of Fields. Fields are a modular way to manage the data of Components.'''

    def __init__(self, path:list[str|int]) -> None:
        '''
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        self.error_path = path

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        '''
        Links this Component to other Components. Returns a list of all children Components (including inline Components) as well as a list of all inline Components.
        Fields are not responsible for calling `set_component` on inline Components.
        :source_component: The Component that owns this Field.
        :components: A dictionary of all Components and with the keys as their names.
        :imported_components: A dictionary with keys of the Component group and values of the imported components from that group.
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
        return "<%s id %i>" % (self.__class__.__name__, id(self))
