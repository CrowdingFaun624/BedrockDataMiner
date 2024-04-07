from typing import Any, Callable, Iterable, Union

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Utilities.TypeVerifier as TypeVerifier

class Component():

    class_name_article = "a Component"
    class_name = "Component"

    my_properties:ComponentCapabilities.Capabilities
    children_has_normalizer_default = False
    type_verifier:TypeVerifier.TypeVerifier

    name: str
    links_to_other_components:list["Component"]
    parents:list["Component"]
    children_has_normalizer:bool

    def __init__(self, data:ComponentTyping.ComponentTypedDicts, name:str, index:int) -> None: ...

    def link_components(self, components:"Component"|Iterable["Component"]) -> None:
        if isinstance(components, Component):
            components = [components]
        self.links_to_other_components.extend(components)
        for component in components:
            component.parents.append(self)

    def set_component(self, components:dict[str,"Component"], functions:dict[str,Callable]) -> None:
        '''Links this Component to other Components'''
        raise NotImplementedError("Class \"%s\" does not have its `set_component` function!" % (self.class_name,))

    def create_final(self) -> None:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        pass

    def link_finals(self) -> None:
        '''Links this Component's final object to other final objects.'''
        pass

    def check(self) -> list[Exception]|None:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        pass

    def finalize_finals(self) -> None:
        '''Can be used to call a method on the final object.'''
        pass

    def propagate_variables(self, child:Union["Component",None]=None) -> None:
        '''Calls `propagates_variables` on the parents of this Component with the child.'''
        has_changed = False
        if child is not None:
            if child.children_has_normalizer and not self.children_has_normalizer:
                self.children_has_normalizer = True
                has_changed = True
        if has_changed or child is None:
            for parent in self.parents:
                parent.propagate_variables(self)

    def get_keys_strs(self, is_capital:bool, keys:list[str|int]) -> str:
        return "".join(
            ("%sey \"%s\" of " % ("K" if index == 0 and is_capital else "k", key)) if isinstance(key, str)
            else ("%stem %i of " % ("I" if index == 0 and is_capital else "i", key))
            for index, key in enumerate(reversed(keys))
        )

    def choose_component(
            self,
            name:str,
            required_properties:ComponentCapabilities.CapabilitiesPattern,
            components:dict[str,"Component"],
            keys:list[str|int],
        ) -> Any:
        if name not in components:
            raise KeyError("%s \"%s\", referenced in %s%s \"%s\", does not exist!" % (required_properties, name, self.get_keys_strs(False, keys), self.class_name, self.name))
        component = components[name]
        if component.my_properties not in required_properties:
            raise ValueError("%s%s \"%s\" references object \"%s\", expecting %s but getting a %s!" % (self.get_keys_strs(True, keys), self.class_name, self.name, name, required_properties, component.my_properties))
        return component

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<%s %s>" % (self.class_name, self.name)
