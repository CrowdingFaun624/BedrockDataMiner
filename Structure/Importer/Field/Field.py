from typing import Callable, Sequence, TypeVar

import Structure.Importer.Component as Component
import Structure.Importer.Pattern as Capabilities
import Utilities.Exceptions as Exceptions


def get_keys_strs(is_capital:bool, keys:list[str|int]) -> str:
    return "".join(
        ("%sey \"%s\" of " % ("K" if index == 0 and is_capital else "k", key)) if isinstance(key, str)
        else ("%stem %i of " % ("I" if index == 0 and is_capital else "i", key))
        for index, key in enumerate(reversed(keys))
    )

a = TypeVar("a")

def choose_component(
        name:str,
        required_properties:Capabilities.Pattern[a],
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        keys:list[str|int],
        component_name:str,
        class_name:str,
    ) -> a:
    component = components.get(name, None)
    if component is None:
        for library in imported_components.values():
            component = library.get(name, None)
            if component is not None:
                break
    if component is None:
        raise Exceptions.UnrecognizedComponentError(name, "%s%s \"%s\"" % (get_keys_strs(False, keys), class_name, component_name), "(should have %r)" % (required_properties,))
    if component.my_capabilities not in required_properties:
        raise Exceptions.InvalidComponentError(component, "%s \"%s\"" % (class_name, component_name), required_properties, component.my_capabilities)
    return component # type: ignore

class Field():
    '''Abstract class of Fields. Fields are a modular way to manage the data of Components.'''

    def __init__(self, path:list[str|int]) -> None:
        '''
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        self.error_path = path

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], imported_components:dict[str,dict[str,"Component.Component"]], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        '''
        Links this Component to other Components.
        :component_name: The name of this Component.
        :component_class_name: the `class_name` attribute of this Component.
        :components: A dictionary of all Components and with the keys as their names.
        :imported_components: A dictionary with keys of the Component group and values of the imported components from that group.
        :functions: A dictionary of functions that is provided by the importer.
        '''
        return []

    def resolve(self) -> None:
        '''
        Used for setting an attribute of this Field that requires a linked Component to be set.
        '''
        ...

    def check(self, component_name:str, component_class_name:str) -> list[Exception]:
        '''
        Make sure that this Component's types are all in order; no error could occur.
        '''
        return []

    def __repr__(self) -> str:
        return "<%s id %i>" % (self.__class__.__name__, id(self))
