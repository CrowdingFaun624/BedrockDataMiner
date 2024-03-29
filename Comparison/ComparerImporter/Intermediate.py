from typing import Any, Callable, Generic, Union

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping

class Intermediate(Generic[ComparerTyping.IntermediateType]):

    def __init__(self, data:ComparerTyping.IntermediateType, name:str, index:int) -> None:
        self.name = name
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.children_has_normalizer = False

    def check_types(self, data:ComparerTyping.IntermediateType, name:str, index:int, allowed_types:list[tuple[str, type|tuple[type,...], str, bool]]) -> None:
        for parameter, parameter_name, allowed_parameter_types, types_str in (
            (data, "data", dict, "a dict"),
            (name, "name", str, "a str"),
            (index, "index", int, "an int"),
        ):
            if not isinstance(parameter, allowed_parameter_types):
                raise TypeError("Parameter \"%s\" of a %s is not a %s!" % (parameter_name, self.__class__.__name__, types_str))
        if len(name) == 0:
            raise ValueError("Parameter \"name\" of %s %i is empty!" % (self.__class__.__name__, index))
        allowed_keys:set[str] = set()
        for key, allowed_type, types_str, is_required in allowed_types:
            allowed_keys.add(key)
            if is_required and key not in data:
                raise KeyError("Key \"%s\" is not in %s \"%s\"!" % (key, self.__class__.__name__, name))
            if key in data and not isinstance(data[key], allowed_type):
                raise TypeError("Key \"%s\" of %s \"%s\" is not %s!" % (key, self.__class__.__name__, name, types_str))
        for key in data:
            if key not in allowed_keys:
                raise KeyError("Key \"%s\" should not exist in %s \"%s\"!" % (key, self.__class__.__name__, name))

    def set(self, intermediate_comparers:dict[str,"Intermediate"], functions:dict[str,Callable]) -> None:
        '''Links this Intermediate to other Intermediates'''
        raise NotImplementedError("Class \"%s\" does not have its `set` function!" % (self.__class__.__name__,))

    def create_final(self) -> None:
        '''Creates this Intermediate's final ComparerSection or Comparer, if applicable.'''
        pass

    def link_finals(self) -> None:
        '''Links this Intermediate's final object to other final objects.'''
        pass

    def check(self) -> list[Exception]|None:
        '''Make sure that this Intermediate's types are all in order; no error could occur.'''
        pass

    def propagate_variables(self, child:Union["Intermediate",None]=None) -> None:
        '''Calls `propagates_variables` on the parents of this intermediate with the child.'''
        has_changed = False
        if child is not None:
            if child.children_has_normalizer and not self.children_has_normalizer:
                self.children_has_normalizer = True
                has_changed = True
        if has_changed or child is None:
            for parent in self.parents:
                parent.propagate_variables(self)

    def choose_intermediate(
            self,
            name:str,
            required_type:type|tuple[type,...],
            required_type_str:str,
            intermediate_comparers:dict[str,"Intermediate"],
            keys:list[str|int],
        ) -> Any:
        get_keys_strs:Callable[[bool],str] = lambda is_capital: "".join(
            ("%sey \"%s\" of " % ("K" if index == 0 and is_capital else "k", key)) if isinstance(key, str)
            else ("%stem %i of " % ("I" if index == 0 and is_capital else "i", key))
            for index, key in enumerate(reversed(keys))
            )
        if name not in intermediate_comparers:
            raise KeyError("%s \"%s\", referenced in %s%s \"%s\", does not exist!" % (required_type_str, name, get_keys_strs(False), self.__class__.__name__, self.name))
        comparer = intermediate_comparers[name]
        if not isinstance(comparer, required_type):
            raise ValueError("%s%s \"%s\" references object \"%s\", expecting %s but getting a %s!" % (get_keys_strs(True), self.__class__.__name__, self.name, name, required_type_str, comparer.__class__.__name__))
        return comparer

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)
