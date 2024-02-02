import json
from typing import Callable, Literal, TypedDict, TypeVar

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
    type: Literal["Main"]

class TypeAliasTypedDict(TypedDict):
    type: Literal["TypeAlias"]
    types: list[str]

class TypedDictComparerTypedDict(TypedDict):
    field: str
    type: Literal["TypedDict"]
    types: list[list[str, str|list[str], str|None]]

ComparerType = dict[str,DictComparerTypedDict|GroupTypedDict|ListComparerTypedDict|MainTypedDict|TypedDictComparerTypedDict]

a = TypeVar("a")
class Intermediate():
    def __init__(self, data:a, name:str, index:int) -> None: ...
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


class DictComparerIntermediate(Intermediate):
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
        self.comparison_move_function = None if "comparison_move_function" not in data else data["comparison_move_function"]
        self.detect_key_moves = False if "detect_key_moves" not in data else data["detect_key_moves"]
        self.field = "field" if "field" not in data else data["field"]
        self.key_types_strs = data["key_types"]
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.value_types_strs = data["value_types"]

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
        self.types = data["types"]

class ListComparerIntermediate(Intermediate):
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

class MainIntermediate(Intermediate):
    def __init__(self, data:MainTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("base_comparer_section", str, "a str", True),
            ("dependencies", list, "a list", False),
            ("normalizer", str, "a str", False),
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
        
        self.name = name
        self.base_comparer_section_str = data["base_comparer_section"]
        self.dependencies = [] if "dependencies" not in data else data["dependencies"]
        self.normalizer_str = None if "normalizer" not in data else data["normalizer"]

class TypedDictIntermediate(Intermediate):
    def __init__(self, data:TypedDictComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("field", str, "a str", False),
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if not all(isinstance(item, list) for item in data["types"]):
            raise TypeError("An item of key \"types\" of TypedDict \"%s\" is not a list!" % name)
        for index, item in enumerate(data["types"]):
            if len(item) != 3:
                raise ValueError("Item %i of key \"types\" of TypedDict \"%s\" is not length 3!" % (index, name))
            if not isinstance(item[0], str):
                raise TypeError("The first item of item %i of key \"types\" of TypedDict \"%s\" is not a str!" % (index, name))
            if not isinstance(item[1], (list, str)):
                raise TypeError("The second item of item %i of key \"types\" of TypedDict \"%s\" is not a list or str!" % (index, name))
            if isinstance(item[1], list):
                for type_index, type_item in enumerate(item[1]):
                    if not isinstance(type_item, str):
                        raise TypeError("Item %i of the second item of item %i of key \"types\" of TypedDict \"%s\" is not a str!" % (type_index, index, name))
            if not isinstance(item[2], str) and item[2] is not None:
                raise TypeError("The third item of item %i of key \"types\" of TypedDict \"%s\" is not a str or None!" % (index, name))

        self.name = name        
        self.field = "field" if "field" not in data else data["field"]
        self.types_strs = data["types"]

def get_file(name:str) -> ComparerType:
    with open(FileManager.get_comparer_path(name), "rt") as f:
        return json.load(f)

def load_from_file(name:str, functions:list[Callable]) -> Comparer.Comparer:
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
    
    # for comparer_name, comparer_intermediate in intermediate_comparers:
    #     comparer_intermediate.set(intermediate_comparers)
