from typing import Any, Callable, Iterable, Union

import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Utilities.TypeVerifier as TypeVerifier

class Intermediate():

    class_name_article = "an Intermediate"
    class_name = "Intermediate"

    my_properties:IntermediateCapabilities.Capabilities
    children_has_normalizer_default = False

    type_verifier:TypeVerifier.TypeVerifier

    def __init__(self, data:ComparerTyping.Intermediates, name:str, index:int) -> None:
        self.name = name
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.children_has_normalizer = False

    def link_intermediates(self, intermediates:"Intermediate"|Iterable["Intermediate"]) -> None:
        if isinstance(intermediates, Intermediate):
            intermediates = [intermediates]
        self.links_to_other_intermediates.extend(intermediates)
        for intermediate in intermediates:
            intermediate.parents.append(self)

    def set(self, intermediate_comparers:dict[str,"Intermediate"], functions:dict[str,Callable]) -> None:
        '''Links this Intermediate to other Intermediates'''
        raise NotImplementedError("Class \"%s\" does not have its `set` function!" % (self.class_name,))

    def create_final(self) -> None:
        '''Creates this Intermediate's final ComparerSection or Comparer, if applicable.'''
        pass

    def link_finals(self) -> None:
        '''Links this Intermediate's final object to other final objects.'''
        pass

    def check(self) -> list[Exception]|None:
        '''Make sure that this Intermediate's types are all in order; no error could occur.'''
        pass

    def finalize_finals(self) -> None:
        '''Can be used to call a method on the final object.'''
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

    def get_keys_strs(self, is_capital:bool, keys:list[str|int]) -> str:
        return "".join(
            ("%sey \"%s\" of " % ("K" if index == 0 and is_capital else "k", key)) if isinstance(key, str)
            else ("%stem %i of " % ("I" if index == 0 and is_capital else "i", key))
            for index, key in enumerate(reversed(keys))
        )

    def choose_intermediate(
            self,
            name:str,
            required_properties:IntermediateCapabilities.CapabilitiesPattern,
            intermediate_comparers:dict[str,"Intermediate"],
            keys:list[str|int],
        ) -> Any:
        if name not in intermediate_comparers:
            raise KeyError("%s \"%s\", referenced in %s%s \"%s\", does not exist!" % (required_properties, name, self.get_keys_strs(False, keys), self.class_name, self.name))
        comparer = intermediate_comparers[name]
        if comparer.my_properties not in required_properties:
            raise ValueError("%s%s \"%s\" references object \"%s\", expecting %s but getting a %s!" % (self.get_keys_strs(True, keys), self.class_name, self.name, name, required_properties, comparer.my_properties))
        return comparer

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<%s %s>" % (self.class_name, self.name)
