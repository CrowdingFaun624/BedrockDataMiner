import json
from typing import Any, Callable, Generator, Iterable, Literal, TypedDict, TypeVar, Union

import Utilities.FileManager as FileManager
import Comparison.Comparer as Comparer

class DictComparerTypedDict(TypedDict):
    comparer: str|None
    comparison_move_function: str
    detect_key_moves: bool
    field: str
    key_types: list[str]
    measure_length: bool
    type: Literal["Dict"]
    value_types: list[str]

class GroupTypedDict(TypedDict):
    type: Literal["Group"]
    types: list[list[str, str|None]]

class ListComparerTypedDict(TypedDict):
    comparer: str|None
    field: str
    measure_length: bool
    ordered: bool
    print_all: bool
    print_flat: bool
    type: Literal["List"]
    types: list[str]

class MainTypedDict(TypedDict):
    base_comparer_section: str
    dependencies: list[str]
    normalizer: str
    post_normalizer: str
    type: Literal["Main"]

class TypeAliasTypedDict(TypedDict):
    type: Literal["TypeAlias"]
    types: list[str]

class TypedDictTypeTypedDict(TypedDict):
    type: str|list[str]
    comparer: str|None

class TypedDictTypeFilledTypedDict(TypedDict):
    type: list[Union[type, "TypeAliasIntermediate"]]
    comparer: Union["ComparerIntermediate", "GroupIntermediate", None]

class TypedDictComparerTypedDict(TypedDict):
    field: str
    measure_length: bool
    type: Literal["TypedDict"]
    types: dict[str,TypedDictTypeTypedDict]

ComparerType = dict[str,DictComparerTypedDict|GroupTypedDict|ListComparerTypedDict|MainTypedDict|TypedDictComparerTypedDict]

DEFAULT_TYPES = {"bool": bool, "dict": dict, "float": float, "int": int, "list": list, "str": str}

a = TypeVar("a")
b = TypeVar("b")
class Intermediate():
    def __init__(self, data:a, name:str, index:int) -> None:
        self.name = name
        self.links_to_other_intermediates:list[Intermediate] = []
    def check_types(self, data:a, name:str, index:int, allowed_types:list[tuple[str, type|tuple[type], str, bool]]) -> None:
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
        for key, allowed_types, types_str, is_required in allowed_types:
            allowed_keys.add(key)
            if is_required and key not in data:
                raise KeyError("Key \"%s\" is not in %s \"%s\"!" % (key, self.__class__.__name__, name))
            if key in data and not isinstance(data[key], allowed_types):
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
    def choose_intermediate(self, name:str, required_type:type[b], required_type_str:str, intermediate_comparers:dict[str,"Intermediate"], keys:list[str]) -> b:
        get_keys_strs:Callable[[bool],str] = lambda is_capital: "".join(
            ("%sey \"%s\" of " % ("K" if index == 0 and is_capital else "k", key)) if isinstance(key, str)
            else ("%stem %i of " % ("I" if index == 0 and is_capital else "i", key))
            for index, key in enumerate(reversed(keys))
            )
        if name not in intermediate_comparers:
            raise KeyError("%s \"%s\", referenced in %s%s \"%s\", does not exist!" % (required_type.__name__, name, get_keys_strs(False), self.__class__.__name__, self.name))
        comparer = intermediate_comparers[name]
        if not isinstance(comparer, required_type):
            raise ValueError("%s%s \"%s\" references object \"%s\", expecting %s but getting a %s!" % (get_keys_strs(True), self.__class__.__name__, self.name, name, required_type_str, comparer.__class__.__name__))
        return comparer
    def __hash__(self) -> int:
        return hash(self.name)

class ComparerIntermediate(Intermediate): # just for type hints lol
    def __init__(self, data: a, name: str, index: int) -> None:
        self.name = name
        self.final:Comparer.ComparerSection = None

class DictComparerIntermediate(ComparerIntermediate):
    def __init__(self, data:DictComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("comparer", (str, type(None)), "a str or None", True),
            ("comparison_move_function", str, "a str", False),
            ("detect_key_moves", bool, "a bool", False),
            ("field", str, "a str", False),
            ("key_types", list, "a list", True),
            ("measure_length", bool, "a bool", False),
            ("type", str, "a str", True),
            ("value_types", list, "a list", True),
        ])
        if data["type"] != "Dict":
            raise ValueError("Key \"type\" of DictComparer \"%s\" is not \"Dict\"!" % (name))
        for key in ("key_types", "value_types"):
            if key not in data: continue
            if len(data[key]) == 0:
                raise ValueError("Key \"%s\" of DictComparer \"%s\" is empty!" % (key, name))
            if not all(isinstance(item, str) for item in data[key]):
                raise TypeError("An item of key \"%s\" of DictComparer \"%s\" is not a str!" % (key, name))
        
        self.name = name
        self.comparer_str = data["comparer"]
        self.comparison_move_function_str = None if "comparison_move_function" not in data else data["comparison_move_function"]
        self.detect_key_moves = False if "detect_key_moves" not in data else data["detect_key_moves"]
        self.field = "field" if "field" not in data else data["field"]
        self.key_types_strs = data["key_types"]
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.value_types_strs = data["value_types"]

        self.comparer:ComparerIntermediate|None = None
        self.comparison_move_function:Callable|None = None
        self.key_types:list[type|TypeAliasIntermediate] = []
        self.value_types:list[type|TypeAliasIntermediate] = []
        self.links_to_other_intermediates:list[Intermediate] = []
        self.final:Comparer.DictComparerSection = None
    
    def choose_types(self, key:str, types_strs:list[str], intermediate_comparers:dict[str,Intermediate]) -> list[Union[type,"TypeAliasIntermediate"]]:
        types:list[type|TypeAliasIntermediate] = []
        already_types:set[str] = set()
        for type_str in types_strs:
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of Dict \"%s\"." % (type_str, key, self.name))
            already_types.add(type_str)
            if type_str in DEFAULT_TYPES:
                types.append(DEFAULT_TYPES[type_str])
            else:
                type_alias = self.choose_intermediate(type_str, TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, [key])
                self.links_to_other_intermediates.append(type_alias)
                types.append(type_alias)
        return types

    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        if self.comparer_str is None:
            self.comparer = None
        else:
            comparer = self.choose_intermediate(self.comparer_str, ComparerIntermediate, "a Comparer", intermediate_comparers, ["comparer"])
            self.links_to_other_intermediates.append(comparer)
            self.comparer = comparer
        if self.comparison_move_function_str is None:
            self.comparison_move_function = None
        else:
            if self.comparison_move_function_str not in functions:
                raise KeyError("Function \"%s\", referenced in key \"comparison_move_function\" of Dict \"%s\", does not exist!" % (self.comparison_move_function_str, self.name))
            self.comparison_move_function = functions[self.comparison_move_function_str]
        self.key_types = self.choose_types("key_types", self.key_types_strs, intermediate_comparers)
        self.value_types = self.choose_types("value_types", self.value_types_strs, intermediate_comparers)
    
    def get_types_final(self, types:list[Union[type,"TypeAliasIntermediate"]]) -> tuple[type]:
        '''Expands a list of types an TypeAliases into just a tuple of types.'''
        output:list[type] = []
        for types_item in types:
            if isinstance(types_item, type):
                output.append(types_item)
            else:
                output.extend(types_item.types)
        return tuple(output)

    def create_final(self) -> None:
        key_types_final = self.get_types_final(self.key_types)
        value_types_final = self.get_types_final(self.value_types)
        self.final = Comparer.DictComparerSection(
            name=self.field,
            comparer=None,
            key_types=key_types_final,
            value_types=value_types_final,
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function,
            measure_length=self.measure_length,
        )
    def link_finals(self) -> None:
        if self.comparer is None:
            self.final.comparer = None
        else:
            self.final.comparer = self.comparer.final

class GroupIntermediate(Intermediate):
    def __init__(self, data:GroupTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if data["type"] != "Group":
            raise ValueError("Key \"type\" of Group \"%s\" is not \"Group\"!" % (name))
        if len(data["types"]) == 0:
            raise ValueError("Key \"types\" of Group \"%s\" is empty!" % (name))
        if not all(isinstance(item, list) for item in data["types"]):
            raise TypeError("An item of key \"types\" in Group \"%s\" is not a list!" % (name))
        if not all(len(item) == 2 for item in data["types"]):
            raise ValueError("An item of key \"types\" in Group \"%s\" is not length 2!" % (name))
        if not all(isinstance(item[0], str) for item in data["types"]):
            raise TypeError("The first item of an item of key \"types\" in Group \"%s\" is not a str!" % (name))
        if not all(isinstance(item[1], str) or item[1] is None for item in data["types"]):
            raise TypeError("The second item of an item of key \"types\" in Group \"%s\" is not a str or None!" % (name))
        
        self.name = name
        self.types_strs = data["types"]

        self.types:list[tuple[type|TypeAliasIntermediate,ComparerIntermediate|None]] = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.final:list[list[Callable[[str,Any],bool], Comparer.ComparerSection|None]] = None
    
    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.types = []
        already_types:set[str] = set()
        for index, (type_str, comparer_str) in enumerate(self.types_strs):
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of Group \"%s\"." % (type_str, self.name))
            already_types.add(type_str)
            if type_str in DEFAULT_TYPES:
                comparer_type = DEFAULT_TYPES[type_str]
            else:
                comparer_type = self.choose_intermediate(type_str, TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, ["types", index])
                self.links_to_other_intermediates.append(comparer_type)
            if comparer_str is None:
                comparer = None
            else:
                comparer = self.choose_intermediate(comparer_str, ComparerIntermediate, "a Comparer", intermediate_comparers, ["types", index])
                self.links_to_other_intermediates.append(comparer)
            self.types.append((comparer_type, comparer))
    
    def create_final(self) -> None:
        self.final = []
    
    def link_finals(self) -> None:
        for comparer_type, comparer_intermediate in self.types:
            if isinstance(comparer_type, type):
                valid_types = comparer_type
            elif isinstance(comparer_type, TypeAliasIntermediate):
                valid_types = tuple(comparer_type.types)
            if comparer_intermediate is None:
                comparer = None
            else:
                comparer = comparer_intermediate.final
            self.final.append((valid_types, comparer))

class ListComparerIntermediate(ComparerIntermediate):
    def __init__(self, data:ListComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("comparer", (str, type(None)), "a str or None", True),
            ("field", str, "a str", False),
            ("measure_length", bool, "a bool", False),
            ("ordered", bool, "a bool", False),
            ("print_all", bool, "a bool", False),
            ("print_flat", bool, "a bool", False),
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if data["type"] != "List":
            raise ValueError("Key \"type\" of ListComparer \"%s\" is not \"List\"!" % (name))
        if len(data["types"]) == 0:
            raise ValueError("Key \"types\" of ListComparer \"%s\" is empty!" % (name))
        if not all(isinstance(item, str) for item in data["types"]):
            raise TypeError("An item of key \"types\" of ListComparer \"%s\" is not a str!" % (name))
        
        self.name = name
        self.comparer_str = data["comparer"]
        self.field = "item" if "field" not in data else data["field"]
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.ordered = True if "ordered" not in data else data["ordered"]
        self.print_all = False if "print_all" not in data else data["print_all"]
        self.print_flat = False if "print_flat" not in data else data["print_flat"]
        self.types_strs = data["types"]

        self.comparer:ComparerIntermediate|None = None
        self.types:list[type|TypeAliasIntermediate] = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.final:Comparer.ListComparerSection = None
    
    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        if self.comparer_str is None:
            self.comparer = None
        else:
            comparer = self.choose_intermediate(self.comparer_str, ComparerIntermediate, "a Comparer", intermediate_comparers, ["comparer"])
            self.links_to_other_intermediates.append(comparer)
            self.comparer = comparer
        self.types = []
        for index, type_str in enumerate(self.types_strs):
            if type_str in DEFAULT_TYPES:
                self.types.append(DEFAULT_TYPES[type_str])
            else:
                type_intermediate = self.choose_intermediate(type_str, TypeAliasIntermediate, "A TypeAlias", intermediate_comparers, ["types", index])
                self.links_to_other_intermediates.append(type_intermediate)
                self.types.append(type_intermediate)
    def create_final(self) -> None:
        types_final:list[type] = []
        for types_item in self.types:
            if isinstance(types_item, type):
                types_final.append(types_item)
            else:
                types_final.extend(types_item.types)
        self.final = Comparer.ListComparerSection(
            name=self.field,
            comparer=None,
            types=tuple(types_final),
            print_flat=self.print_flat,
            print_all=self.print_all,
            measure_length=self.measure_length,
            ordered=self.ordered,
        )
    def link_finals(self) -> None:
        if self.comparer is None:
            self.final.comparer = None
        else:
            self.final.comparer = self.comparer.final

class MainIntermediate(Intermediate):
    def __init__(self, data:MainTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("base_comparer_section", str, "a str", True),
            ("dependencies", list, "a list", False),
            ("normalizer", str, "a str", False),
            ("post_normalizer", str, "a str", False),
            ("type", str, "a str", True),
        ])
        if data["type"] != "Main":
            raise ValueError("Key \"type\" of Main \"%s\" is not \"Main\"!" % (name))
        if "dependencies" in data and not all(isinstance(item, str) for item in data["dependencies"]):
            raise TypeError("An item of key \"dependencies\" of Main \"%s\" is not a str!" % (name))
        
        self.name = name
        self.base_comparer_section_str = data["base_comparer_section"]
        self.dependencies = [] if "dependencies" not in data else data["dependencies"]
        self.normalizer_str = None if "normalizer" not in data else data["normalizer"]
        self.post_normalizer_str = None if "post_normalizer" not in data else data["post_normalizer"]

        self.base_comparer_section:ComparerIntermediate = None
        self.normalizer:Callable|None = None
        self.post_normalizer:Callable|None = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.final:Comparer.Comparer = None
    
    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.base_comparer_section = self.choose_intermediate(self.base_comparer_section_str, ComparerIntermediate, "a Comparer", intermediate_comparers, ["base_comparer_section"])
        self.links_to_other_intermediates.append(self.base_comparer_section)
        if self.normalizer_str is None:
            self.normalizer = None
        else:
            if self.normalizer_str not in functions:
                raise KeyError("Function \"%s\", referenced in key \"normalizer\" of Main \"%s\", does not exist!" % (self.normalizer_str, self.name))
            self.normalizer = functions[self.normalizer_str]
        if self.post_normalizer_str is None:
            self.post_normalizer = None
        else:
            if self.post_normalizer_str not in functions:
                raise KeyError("Function \"%s\", referenced in key \"post_normalizer\" of Main \"%s\", does not exist!" % (self.normalizer_str, self.name))
            self.post_normalizer = functions[self.post_normalizer_str]
    
    def create_final(self) -> None:
        self.final = Comparer.Comparer(
            normalizer=self.normalizer,
            post_normalizer=self.post_normalizer,
            dependencies=self.dependencies,
            base_comparer_section=None,
        )
    def link_finals(self) -> None:
        self.final.base_comparer_section = self.base_comparer_section.final

class TypeAliasIntermediate(Intermediate):
    def __init__(self, data:TypeAliasTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if data["type"] != "TypeAlias":
            raise ValueError("Key \"type\" of TypeAlias \"%s\" is not \"TypeAlias\"!" % (name))
        if "dependencies" in data and not all(isinstance(item, str) for item in data["dependencies"]):
            raise TypeError("An item of key \"dependencies\" of TypeAlias \"%s\" is not a str!" % (name))
        if name in ("dict", "float", "int", "list", "str"):
            raise ValueError("TypeAlias \"%s\" has an invalid name!" % name)
        
        self.name = name
        self.types_strs = data["types"]

        self.types:list[type] = None
    
    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.types = []
        already_types:set[str] = set()
        for type_str in self.types_strs:
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of TypeAlias \"%s\"." % (type_str, self.name))
            already_types.add(type_str)
            if type_str in DEFAULT_TYPES:
                self.types.append(DEFAULT_TYPES[type_str])
            else:
                raise KeyError("TypeAlias refers to type \"%s\", which is not a valid default type!" % type_str)

class TypedDictIntermediate(ComparerIntermediate):
    def __init__(self, data:TypedDictComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("field", str, "a str", False),
            ("measure_length", bool, "a bool", False),
            ("type", str, "a str", True),
            ("types", dict, "a dict", True),
        ])
        if not all(isinstance(value, dict) for value in data["types"].values()):
            raise TypeError("A value of key \"types\" of TypedDict \"%s\" is not a dict!" % name)
        for key, value in data["types"].items():
            if not isinstance(value, dict):
                raise TypeError("Item %s of key \"types\" of TypedDict \"%s\" is not a dict!" % (key, name))
            for value_key, value_value in value.items():
                match value_key:
                    case "type":
                        if not isinstance(value_value, (list, str)):
                            raise TypeError("Key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a list or str!" % (value_key, key, name))
                        if isinstance(value_value, list):
                            for type_index, type_item in enumerate(value_value):
                                if not isinstance(type_item, str):
                                    raise TypeError("Item %i of the key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a str!" % (type_index, value_key, key, name))
                    case "comparer":
                        if not (isinstance(value_value, str) or value_value is None):
                            raise TypeError("Key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a str or None!" % (value_key, key, name))
                    case _:
                        raise KeyError("Key \"%s\" of key \"%s\" of \"types\" of TypedDict \"%s\" is not a valid key!" % (value_key, key, name))
            for required_key in ("type", "comparer"):
                if required_key not in value:
                    raise KeyError("Key \"%s\" of key \"types\" of TypedDict \"%s\" does not have the required key \"%s\"!" % (key, name, required_key))

        self.name = name        
        self.field = "field" if "field" not in data else data["field"]
        self.types_strs = data["types"]
        self.types:dict[str,TypedDictTypeFilledTypedDict] = None
        self.measure_length = False if "measure_length" not in data else data["measure_length"]

        self.links_to_other_intermediates:list[Intermediate] = []
        self.final:Comparer.DictComparerSection = None
    
    def choose_types_type_iterator(self, data:TypedDictTypeTypedDict) -> Generator[tuple[int|None, str], None, None]:
        '''Yields the index of the type_str and the type_str, or None and the type_str if it is not a list'''
        if isinstance(data["type"], str):
            yield (None, data["type"])
        else:
            yield from enumerate(data["type"])

    def choose_types(self, key:str, data:TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate]) -> list[type|TypeAliasIntermediate]:
        types:list[type] = []
        already_keys:set[str] = set()
        for index, type_str in self.choose_types_type_iterator(data):
            if type_str in already_keys:
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of TypedDict \"%s\"." % (type_str, key, self.name))
            already_keys.add(type_str)

            if type_str in DEFAULT_TYPES:
                types.append(DEFAULT_TYPES[type_str])
            else:
                choose_comparer_keys = ["types", key, "type"] if index is None else ["types", key, "type", index]
                type_intermediate = self.choose_intermediate(type_str, TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, choose_comparer_keys)
                self.links_to_other_intermediates.append(type_intermediate)
                types.append(type_intermediate)
        return types
        
    def set_comparer(self, key:str, data:TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate]) -> ComparerIntermediate|None:
        if data["comparer"] is None: return None
        comparer = self.choose_intermediate(data["comparer"], ComparerIntermediate|GroupIntermediate, "a Comparer or Group", intermediate_comparers, ["types", key, "comparer"])
        self.links_to_other_intermediates.append(comparer)
        return comparer
    
    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.types = {}
        for key, data in self.types_strs.items():
            self.types[key] = {
                "comparer": self.set_comparer(key, data, intermediate_comparers),
                "type": self.choose_types(key, data, intermediate_comparers),
            }
    
    def create_final(self) -> None:
        self.final = Comparer.DictComparerSection(
            name=self.field,
            comparer=None,
            key_types=None,
            value_types=None,
            measure_length=self.measure_length
        )
    def link_finals(self) -> None:
        types_final:list[tuple[str, type|list[type], Comparer.ComparerSection|None]] = []
        for key, data in self.types.items():
            types:list[type] = []
            for types_item in data["type"]:
                if isinstance(types_item, type):
                    types.append(types_item)
                else:
                    types.extend(types_item.types)
            if len(types) == 1:
                types = types[0]
            else:
                types = tuple(types)
            if data["comparer"] is None:
                comparer = None
            else:
                comparer = data["comparer"].final
            types_final.append((key, types, comparer))
        Comparer.type_check_TypedDictComparerSection_parameters(self.field, types_final)
        key_types_lambda, value_types_lambda, all_comparers = Comparer.get_TypedDictComparerSection_attributes(self.field, types_final)
        self.final.key_types = key_types_lambda
        self.final.value_types = value_types_lambda
        self.final.comparer = all_comparers

def get_file(name:str) -> ComparerType:
    with open(FileManager.get_comparer_path(name), "rt") as f:
        return json.load(f)

def get_used_intermediates(main_comparer:MainIntermediate) -> set[Intermediate]:
    visited_nodes:set[Intermediate] = set()
    unvisited_nodes:list[Intermediate] = [main_comparer]
    while len(unvisited_nodes) > 0:
        unvisited_node = unvisited_nodes.pop()
        if unvisited_node in visited_nodes: continue
        for neighbor in unvisited_node.links_to_other_intermediates:
            if neighbor in visited_nodes:
                continue
            else:
                unvisited_nodes.append(neighbor)
        visited_nodes.add(unvisited_node)
    return visited_nodes

def get_link_final_order(intermediate_comparers:Iterable[Intermediate]) -> Generator[Intermediate, None, None]:
    intermediate_types:dict[type[Intermediate], list[Intermediate]] = {
        DictComparerIntermediate: [],
        GroupIntermediate: [],
        ListComparerIntermediate: [],
        MainIntermediate: [],
        TypeAliasIntermediate: [],
        TypedDictIntermediate: [],
    }
    for intermediate in intermediate_comparers:
        intermediate_types[type(intermediate)].append(intermediate)
    for intermediates in intermediate_types.values():
        yield from intermediates

def load_from_file(name:str, functions:dict[str,Callable]) -> Comparer.Comparer:
    if not isinstance(name, str):
        raise TypeError("`name` is not a str!")
    if not isinstance(functions, dict):
        raise TypeError("`functions` of `load_from_file` \"%s\" is not a dict!" % (name))
    for index, (key, value) in enumerate(functions.items()):
        if not isinstance(key, str):
            raise TypeError("Key of index %i of `functions` of `load_from_file` \"%s\" is not a str!" % (index, name))
        if not isinstance(value, Callable):
            raise TypeError("Value of key \"%s\" of `functions` of `load_from_file` \"%s\" is not a Callable!" % (key, name))
    
    data = get_file(name)
    if not isinstance(data, dict):
        raise TypeError("Comparer file \"%s\" is not a dict!" % (name))
    intermediate_comparers:dict[str,Intermediate] = {}
    main_comparers:list[tuple[str,MainIntermediate]] = []
    for index, (comparer_name, comparer_data) in enumerate(data.items()):
        if not isinstance(comparer_name, str):
            raise TypeError("Comparer index %i's name is not a str!" % (index))
        if not isinstance(comparer_data, dict):
            raise TypeError("Comparer \"%s\" is not a dict!" % (comparer_name))
        if "type" not in comparer_data:
            raise KeyError("Comparer \"%s\" has no \"type\" key!" % (comparer_name))
        if not isinstance(comparer_data["type"], str):
            raise TypeError("Key \"type\" of Comparer \"%s\" is not a str!" % (comparer_name))
        match comparer_data["type"]:
            case "Dict":
                intermediate_comparers[comparer_name] = DictComparerIntermediate(comparer_data, comparer_name, index)
            case "Group":
                intermediate_comparers[comparer_name] = GroupIntermediate(comparer_data, comparer_name, index)
            case "List":
                intermediate_comparers[comparer_name] = ListComparerIntermediate(comparer_data, comparer_name, index)
            case "Main":
                comparer = MainIntermediate(comparer_data, comparer_name, index)
                intermediate_comparers[comparer_name] = comparer
                main_comparers.append((comparer_name, comparer))
            case "TypedDict":
                intermediate_comparers[comparer_name] = TypedDictIntermediate(comparer_data, comparer_name, index)
            case _:
                raise ValueError("Comparer \"%s\" has an invalid \"type\" key: %s" % (comparer_name, comparer_data["type"]))
    if len(main_comparers) == 0:
        raise ValueError("There is not a Main comparer in Comparer file \"%s\"!" % name)
    if len(main_comparers) > 1:
        raise ValueError("There are more than one Main comparer in Comparer file \"%s\": [%s]" % (", ".join(comparer_name for comparer_name, comparer_intermediate in main_comparers)))
    
    main_comparer = main_comparers[0][1]
    for comparer_name, comparer_intermediate in intermediate_comparers.items():
        comparer_intermediate.set(intermediate_comparers, functions)

    used_intermediates = get_used_intermediates(main_comparer)
    unused_intermediates = [intermediate for intermediate in intermediate_comparers.values() if intermediate not in used_intermediates]
    if len(unused_intermediates) > 0:
        print("Warning: Comparer file \"%s\" has %i unused comparers: %s" % (name, len(unused_intermediates), [intermediate.name for intermediate in unused_intermediates]))
    
    for comparer_intermediate in intermediate_comparers.values():
        comparer_intermediate.create_final()
    for comparer_intermediate in get_link_final_order(intermediate_comparers.values()):
        comparer_intermediate.link_finals()

    return main_comparer.final
