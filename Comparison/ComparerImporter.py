import json
from types import UnionType
from typing import Callable, Generator, Generic, Iterable, Literal, TypedDict, TypeVar, Union

import Comparison.Comparer as Comparer
import Comparison.ComparerFunctions as ComparerFunctions
import Comparison.ComparerSection as ComparerSection
import Comparison.DictComparerSection as DictComparerSection
import Comparison.ListComparerSection as ListComparerSection
import Comparison.Normalizer as Normalizer
import Comparison.TypedDictComparerSection as TypedDictComparerSection
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller, WaitValue

NoneType = type(None)

class DictComparerTypedDict(TypedDict):
    comparer: str|None
    comparison_move_function: str
    detect_key_moves: bool
    field: str
    measure_length: bool
    normalizer: str|list[str]
    type: Literal["Dict"]
    print_all: bool
    types: list[str]

class GroupTypedDict(TypedDict):
    type: Literal["Group"]
    types: dict[str,str|None]

class ListComparerTypedDict(TypedDict):
    comparer: str|None
    field: str
    measure_length: bool
    normalizer: str|list[str]
    ordered: bool
    print_all: bool
    print_flat: bool
    type: Literal["List"]
    types: list[str]

ComponentTypedDict = TypedDict("ComponentTypedDict", {"as": str, "component": str})

ImportTypedDict = TypedDict("ImportTypedDict", {"from": str, "components": list[ComponentTypedDict]})

class MainTypedDict(TypedDict):
    base_comparer_section: str
    imports: list[ImportTypedDict]
    normalizer: str
    post_normalizer: str
    type: Literal["Main"]

class NormalizerFunctionTypedDict(TypedDict):
    dependencies: list[str]
    function_name: str
    type: Literal["NormalizerFunction"]

class TypeAliasTypedDict(TypedDict):
    type: Literal["TypeAlias"]
    types: list[str]

class TypedDictTypeTypedDict(TypedDict):
    type: str|list[str]
    comparer: str|None
    normalizer: str|list[str]
    tags: list[str]

class TypedDictTypeFilledTypedDict(TypedDict):
    type: list[Union[type, "TypeAliasIntermediate"]]
    comparer: Union["ComparerIntermediate", "GroupIntermediate", None]
    tags: list[str]

class TypedDictComparerTypedDict(TypedDict):
    field: str
    measure_length: bool
    normalizer: str
    type: Literal["TypedDict"]
    types: dict[str,TypedDictTypeTypedDict]

Intermediates = DictComparerTypedDict|GroupTypedDict|ListComparerTypedDict|MainTypedDict|NormalizerFunctionTypedDict|TypeAliasTypedDict|TypedDictComparerTypedDict
Comparers = DictComparerTypedDict|ListComparerTypedDict|TypedDictComparerTypedDict
ComparerType = dict[str,Intermediates]

DEFAULT_TYPES:dict[str,type] = {"bool": bool, "dict": dict, "float": float, "int": int, "list": list, "null": type(None), "str": str}
REQUIRES_COMPARER_TYPES = set([dict, list])

IntermediateType = TypeVar("IntermediateType", DictComparerTypedDict, GroupTypedDict, ListComparerTypedDict, MainTypedDict, NormalizerFunctionTypedDict, TypeAliasTypedDict, TypedDictComparerTypedDict)
ComparerType = TypeVar("ComparerType", DictComparerTypedDict, ListComparerTypedDict, TypedDictComparerTypedDict)
ChooseIntermediateType = TypeVar("ChooseIntermediateType", DictComparerTypedDict, GroupTypedDict, ListComparerTypedDict, MainTypedDict, NormalizerFunctionTypedDict, TypeAliasTypedDict, TypedDictComparerTypedDict)

class Intermediate(Generic[IntermediateType]):

    def __init__(self, data:IntermediateType, name:str, index:int) -> None:
        self.name = name
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.children_has_normalizer = False

    def check_types(self, data:IntermediateType, name:str, index:int, allowed_types:list[tuple[str, tuple[type,...], str, bool]]) -> None:
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

    def check(self) -> None:
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
            required_type:type[ChooseIntermediateType],
            required_type_str:str,
            intermediate_comparers:dict[str,"Intermediate"],
            keys:list[str|int],
        ) -> ChooseIntermediateType:
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

class ComparerIntermediate(Intermediate[ComparerType]): # just for type hints lol

    my_type:list[type]

    def __init__(self, data: ComparerType, name: str, index: int) -> None:
        self.name = name
        self.final:ComparerSection.ComparerSection|None = None

class DictComparerIntermediate(ComparerIntermediate):

    my_type = [dict]

    def __init__(self, data:DictComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("comparer", (str, type(None)), "a str or None", True),
            ("comparison_move_function", str, "a str", False),
            ("detect_key_moves", bool, "a bool", False),
            ("field", str, "a str", False),
            ("measure_length", bool, "a bool", False),
            ("normalizer", (str, list), "a str or list", False),
            ("print_all", bool, "a bool", False),
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if data["type"] != "Dict":
            raise ValueError("Key \"type\" of DictComparer \"%s\" is not \"Dict\"!" % (name))
        if len(data["types"]) == 0:
            raise ValueError("Key \"types\" of DictComparer \"%s\" is empty!" % (name))
        if not all(isinstance(item, str) for item in data["types"]):
            raise TypeError("An item of key \"types\" of DictComparer \"%s\" is not a str!" % (name))
        if "normalizer" in data and isinstance(data["normalizer"], list):
            if not all(isinstance(item, str) for item in data["normalizer"]):
                raise TypeError("An item of key \"normalizer\" of DictComparer \"%s\" is not a str!" % (name))

        self.name = name
        self.comparer_str = data["comparer"]
        self.comparison_move_function_str = None if "comparison_move_function" not in data else data["comparison_move_function"]
        self.detect_key_moves = False if "detect_key_moves" not in data else data["detect_key_moves"]
        self.field = "field" if "field" not in data else data["field"]
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = False if "print_all" not in data else data["print_all"]
        self.types_strs = data["types"]

        self.comparer:ComparerIntermediate|GroupIntermediate|None = None
        self.comparison_move_function:Callable|None = None
        self.normalizers:list[NormalizerFunctionIntermediate]|None = None
        self.types:list[type|TypeAliasIntermediate] = []
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.types_final:list[type] = None
        self.final:DictComparerSection.DictComparerSection = None
        
        self.children_has_normalizer = False

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
            comparer:ComparerIntermediate|GroupIntermediate = self.choose_intermediate(self.comparer_str, ComparerIntermediate|GroupIntermediate, "a Comparer or Group", intermediate_comparers, ["comparer"])
            self.links_to_other_intermediates.append(comparer)
            comparer.parents.append(self)
            self.comparer = comparer
        if self.comparison_move_function_str is None:
            self.comparison_move_function = None
        else:
            if self.comparison_move_function_str not in functions:
                raise KeyError("Function \"%s\", referenced in key \"comparison_move_function\" of Dict \"%s\", does not exist!" % (self.comparison_move_function_str, self.name))
            self.comparison_move_function = functions[self.comparison_move_function_str]
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerFunctionIntermediate] = [self.choose_intermediate(normalizer_str, NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_intermediates.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)
        self.types = self.choose_types("types", self.types_strs, intermediate_comparers)

    def get_types_final(self, types:list[Union[type,"TypeAliasIntermediate"]]) -> tuple[type,...]:
        '''Expands a list of types an TypeAliases into just a tuple of types.'''
        output:list[type] = []
        for types_item in types:
            if isinstance(types_item, type):
                output.append(types_item)
            else:
                output.extend(types_item.types)
        return tuple(output)

    def create_final(self) -> None:
        self.types_final = self.get_types_final(self.types)
        normalizer_final = None if self.normalizers is None else [normalizer.final for normalizer in self.normalizers]
        self.final = DictComparerSection.DictComparerSection(
            name=self.field,
            comparer=None,
            types=self.types_final,
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
        )
    
    def link_finals(self) -> None:
        if self.comparer is None:
            self.final.comparer = None
        else:
            self.final.comparer = self.comparer.final
    
    def check(self) -> None:
        self.final.check_initialization_parameters()
        if self.comparer is None:
            for value_type in self.types_final:
                if value_type in REQUIRES_COMPARER_TYPES:
                    raise TypeError("DictComparer \"%s\" accepts type %s, but has a null comparer!" % (self.name, value_type.__name__))
        else:
            for value_type in self.types_final:
                if value_type not in self.comparer.my_type:
                    its_types = ", ".join(type_item.__name__ for type_item in self.comparer.my_type)
                    raise TypeError("DictComparer \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (self.name, value_type.__name__, self.comparer.name, its_types))

class GroupIntermediate(Intermediate):

    def __init__(self, data:GroupTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("type", str, "a str", True),
            ("types", dict, "a dict", True),
        ])
        if data["type"] != "Group":
            raise ValueError("Key \"type\" of Group \"%s\" is not \"Group\"!" % (name))
        if len(data["types"]) == 0:
            raise ValueError("Key \"types\" of Group \"%s\" is empty!" % (name))
        if not all(isinstance(key, str) for key in data["types"].keys()):
            raise TypeError("A key of key \"types\" in Group \"%s\" is not a str!" % (name))
        if not all(isinstance(value, str) or value is None for value in data["types"].values()):
            raise TypeError("A value of key \"types\" in Group \"%s\" is not a str or None!" % (name))

        self.name = name
        self.types_strs = data["types"]

        self.types:list[tuple[type|TypeAliasIntermediate,ComparerIntermediate|None]] = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.my_type:set[type] = set()
        self.check_types_final:list[tuple[list[type], ComparerIntermediate]] = None
        self.final:dict[type,ComparerSection.ComparerSection] = None

        self.children_has_normalizer = False

    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.types = []
        already_types:set[str] = set()
        for type_str, comparer_str in self.types_strs.items():
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of Group \"%s\"." % (type_str, self.name))
            already_types.add(type_str)
            if type_str in DEFAULT_TYPES:
                comparer_type = DEFAULT_TYPES[type_str]
                self.my_type.add(comparer_type)
            else:
                comparer_type = self.choose_intermediate(type_str, TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, ["types", type_str])
                self.links_to_other_intermediates.append(comparer_type)
                comparer_type.parents.append(self)
                self.my_type.update(comparer_type.types)
            if comparer_str is None:
                comparer = None
            else:
                comparer = self.choose_intermediate(comparer_str, ComparerIntermediate, "a Comparer", intermediate_comparers, ["types", type_str])
                self.links_to_other_intermediates.append(comparer)
                comparer.parents.append(self)
            self.types.append((comparer_type, comparer))
    
    def create_final(self) -> None:
        self.final = {}

    def link_finals(self) -> None:
        self.check_types_final = []
        for comparer_type, comparer_intermediate in self.types:
            if isinstance(comparer_type, type):
                valid_types = [comparer_type]
            elif isinstance(comparer_type, TypeAliasIntermediate):
                valid_types = comparer_type.types
            if comparer_intermediate is None:
                comparer_final = None
            else:
                comparer_final = comparer_intermediate.final
            for valid_type in valid_types:
                self.final[valid_type] = comparer_final
            self.check_types_final.append((valid_types, comparer_intermediate))

    def check(self) -> None:
        for index, (types, comparer) in enumerate(self.check_types_final):
            if comparer is None:
                for type_item in types:
                    if type_item in REQUIRES_COMPARER_TYPES:
                        raise TypeError("Item %i of Group \"%s\" accepts type %s, but has a null comparer!" % (index, self.name, type_item.__name__))
            else:
                for type_item in types:
                    if type_item not in comparer.my_type:
                        its_types = ", ".join(its_type.__name__ for its_type in comparer.my_type)
                        raise TypeError("Item %i of Group \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (index, self.name, type_item.__name__, comparer.name, its_types))

class ListComparerIntermediate(ComparerIntermediate):

    my_type = [list]

    def __init__(self, data:ListComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("comparer", (str, type(None)), "a str or None", True),
            ("field", str, "a str", False),
            ("measure_length", bool, "a bool", False),
            ("normalizer", (str, list), "a str or list", False),
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
        if "normalizer" in data and isinstance(data["normalizer"], list):
            if not all(isinstance(item, str) for item in data["normalizer"]):
                raise TypeError("An item of key \"normalizer\" of ListComparer \"%s\" is not a str!" % (name))

        self.name = name
        self.comparer_str = data["comparer"]
        self.field = "item" if "field" not in data else data["field"]
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.ordered = True if "ordered" not in data else data["ordered"]
        self.print_all = False if "print_all" not in data else data["print_all"]
        self.print_flat = False if "print_flat" not in data else data["print_flat"]
        self.types_strs = data["types"]

        self.comparer:ComparerIntermediate|GroupIntermediate|None = None
        self.types:list[type|TypeAliasIntermediate] = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.normalizers:list[NormalizerFunctionIntermediate]|None = None
        self.types_final:list[type] = []
        self.final:ListComparerSection.ListComparerSection = None
        
        self.children_has_normalizer = False

    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        if self.comparer_str is None:
            self.comparer = None
        else:
            comparer:ComparerIntermediate|GroupIntermediate = self.choose_intermediate(self.comparer_str, ComparerIntermediate|GroupIntermediate, "a Comparer or Group", intermediate_comparers, ["comparer"])
            self.links_to_other_intermediates.append(comparer)
            comparer.parents.append(self)
            self.comparer = comparer
        self.types = []
        for index, type_str in enumerate(self.types_strs):
            if type_str in DEFAULT_TYPES:
                self.types.append(DEFAULT_TYPES[type_str])
            else:
                type_intermediate:TypeAliasIntermediate = self.choose_intermediate(type_str, TypeAliasIntermediate, "A TypeAlias", intermediate_comparers, ["types", index])
                self.links_to_other_intermediates.append(type_intermediate)
                type_intermediate.parents.append(self)
                self.types.append(type_intermediate)
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerFunctionIntermediate] = [self.choose_intermediate(normalizer_str, NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_intermediates.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)
    
    def create_final(self) -> None:
        self.types_final:list[type] = []
        for types_item in self.types:
            if isinstance(types_item, type):
                self.types_final.append(types_item)
            else:
                self.types_final.extend(types_item.types)
        normalizer_final = None if self.normalizers is None else [normalizer.final for normalizer in self.normalizers]
        self.final = ListComparerSection.ListComparerSection(
            name=self.field,
            comparer=None,
            types=tuple(self.types_final),
            print_flat=self.print_flat,
            print_all=self.print_all,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            ordered=self.ordered,
            children_has_normalizer=self.children_has_normalizer,
        )

    def link_finals(self) -> None:
        if self.comparer is None:
            self.final.comparer = None
        else:
            self.final.comparer = self.comparer.final

    def check(self) -> None:
        self.final.check_initialization_parameters()
        if self.comparer is None:
            for value_type in self.types_final:
                if value_type in REQUIRES_COMPARER_TYPES:
                    raise TypeError("ListComparer \"%s\" accepts type %s, but has a null comparer!" % (self.name, value_type.__name__))
        else:
            for value_type in self.types_final:
                if value_type not in self.comparer.my_type:
                    its_types = ", ".join(type_item.__name__ for type_item in self.comparer.my_type)
                    raise TypeError("ListComparer \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (self.name, value_type.__name__, self.comparer.name, its_types))

class MainIntermediate(Intermediate):

    def __init__(self, data:MainTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("base_comparer_section", str, "a str", True),
            ("imports", list, "a list", False),
            ("name", str, "a str", True),
            ("normalizer", str, "a str", False),
            ("post_normalizer", str, "a str", False),
            ("type", str, "a str", True),
        ])
        if data["type"] != "Main":
            raise ValueError("Key \"type\" of Main \"%s\" is not \"Main\"!" % (name))
        if "dependencies" in data and not all(isinstance(item, str) for item in data["dependencies"]):
            raise TypeError("An item of key \"dependencies\" of Main \"%s\" is not a str!" % (name))
        if "imports" in data:
            if not isinstance(data["imports"], list):
                raise TypeError("Key \"imports\" is not a list!")
            self.check_imports_type(data["imports"], name)

        self.name = name
        self.comparer_name = data["name"]
        self.base_comparer_section_str = data["base_comparer_section"]
        self.normalizer_str = None if "normalizer" not in data else data["normalizer"]
        self.post_normalizer_str = None if "post_normalizer" not in data else data["post_normalizer"]
        self.imports = None if "imports" not in data else data["imports"]

        self.base_comparer_section:ComparerIntermediate = None
        self.normalizer:NormalizerFunctionIntermediate|None = None
        self.post_normalizer:NormalizerFunctionIntermediate|None = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.final:Comparer.Comparer = None

        self.children_has_normalizer = False

    def check_imports_type(self, imports:list[ImportTypedDict], name:str) -> None:
        for index, imported_comparer in enumerate(imports):
            if not isinstance(imported_comparer, dict):
                raise TypeError("Item %i of key \"imports\" of Main \"%s\" is not a dict!" % (index, name))
            unrecognized_keys = [key for key in imported_comparer.keys() if key not in ("from", "components")]
            if len(unrecognized_keys) > 0:
                raise KeyError("Unrecognized key(s) in item %i of key \"imports\" of Main \"%s\": [%s]" % (index, name, ", ".join(unrecognized_keys)))
            if "from" not in imported_comparer:
                raise KeyError("Key \"from\" is not in item %i of key \"imports\" of Main \"%s\"!" % (index, name))
            if "components" not in imported_comparer:
                raise KeyError("Key \"components\" is not in item %i of key \"imports\" of Main \"%s\"!" % (index, name))
            if not isinstance(imported_comparer["from"], str):
                raise TypeError("Key \"from\" of item %i of key \"imports\" of Main \"%s\" is not a str!" % (index, name))
            if not isinstance(imported_comparer["components"], list):
                raise TypeError("Key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a list!" % (index, name))
            for component_index, imported_component in enumerate(imported_comparer["components"]):
                if not isinstance(imported_component, dict):
                    raise TypeError("Item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a dict!" % (component_index, index, name))
                unrecognized_keys = [key for key in imported_component.keys() if key not in ("component", "as")]
                if len(unrecognized_keys) > 0:
                    raise KeyError("Unrecognized key(s) in item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\": [%s]" % (component_index, index, name, ", ".join(unrecognized_keys)))
                if "component" not in imported_component:
                    raise KeyError("Key \"component\" is not in item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\"!" % (component_index, index, name))
                if not isinstance(imported_component["component"], str):
                    raise TypeError("Key \"component\" of item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a str!" % (component_index, index, name))
                if "as" in imported_component and not isinstance(imported_component["as"], str):
                    raise TypeError("Key \"as\" of item %i of key \"components\" of item %i of key \"imports\" of Main \"%s\" is not a str!" % (component_index, index, name))

    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.base_comparer_section:ComparerIntermediate = self.choose_intermediate(self.base_comparer_section_str, ComparerIntermediate, "a Comparer", intermediate_comparers, ["base_comparer_section"])
        self.links_to_other_intermediates.append(self.base_comparer_section)
        self.base_comparer_section.parents.append(self)
        if self.normalizer_str is None:
            self.normalizer = None
        else:
            self.normalizer:NormalizerFunctionIntermediate = self.choose_intermediate(self.normalizer_str, NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"])
            self.links_to_other_intermediates.append(self.normalizer)
            self.normalizer.parents.append(self)
        if self.post_normalizer_str is None:
            self.post_normalizer = None
        else:
            self.post_normalizer:NormalizerFunctionIntermediate = self.choose_intermediate(self.post_normalizer_str, NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["post_normalizer"])
            self.links_to_other_intermediates.append(self.post_normalizer)
            self.post_normalizer.parents.append(self)
    
    def create_final(self) -> None:
        normalizer_final = None if self.normalizer is None else self.normalizer.final
        post_normalizer_final = None if self.post_normalizer is None else self.post_normalizer.final
        self.final = Comparer.Comparer(
            name=self.comparer_name,
            normalizer=normalizer_final,
            post_normalizer=post_normalizer_final,
            base_comparer_section=None,
        )
    
    def link_finals(self) -> None:
        self.final.base_comparer_section = self.base_comparer_section.final

class NormalizerFunctionIntermediate(Intermediate):

    def __init__(self, data:NormalizerFunctionTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("dependencies", list, "a list", True),
            ("function_name", str, "a str", True),
            ("type", str, "a str", True),
        ])
        if data["type"] != "NormalizerFunction":
            raise ValueError("Key \"type\" of Main \"%s\" is not \"Main\"!" % (name))
        if not all(isinstance(item, str) for item in data["dependencies"]):
            raise TypeError("An item of key \"dependencies\" of NormalizerFunction \"%s\" is not a str!" % (name))
        
        self.name = name
        self.dependencies = data["dependencies"]
        self.function_name = data["function_name"]

        self.final:Normalizer.Normalizer = None
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []

        self.children_has_normalizer = True
    
    def set(self, intermediate_comparers: dict[str, Intermediate], functions: dict[str, Callable]) -> None:
        if self.function_name not in functions:
            raise KeyError("Function \"%s\", referenced in key \"function_name\" of NormalizerFunction \"%s\", does not exist!" % (self.function_name, self.name))
        self.final = Normalizer.Normalizer(functions[self.function_name], self.dependencies)

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
        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []

        self.children_has_normalizer = False

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

    my_type = [dict]

    def __init__(self, data:TypedDictComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("field", str, "a str", False),
            ("measure_length", bool, "a bool", False),
            ("normalizer", (str, list), "a str or list", False),
            ("print_all", bool, "a bool", False),
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
                    case "tags":
                        if not isinstance(value_value, list):
                            raise TypeError("Key \"%s\" of key \"%s\" of key \"types \" of TypedDict \"%s\" is not a list!" % (value_key, key, name))
                        for tag_index, tag_item in enumerate(value_value):
                            if not isinstance(tag_item, str):
                                raise TypeError("Item %i of key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a str!" % (tag_index, value_key, key, name))
                    case _:
                        raise KeyError("Key \"%s\" of key \"%s\" of \"types\" of TypedDict \"%s\" is not a valid key!" % (value_key, key, name))
            for required_key in ("type",):
                if required_key not in value:
                    raise KeyError("Key \"%s\" of key \"types\" of TypedDict \"%s\" does not have the required key \"%s\"!" % (key, name, required_key))
        if "normalizer" in data and isinstance(data["normalizer"], list):
            if not all(isinstance(item, str) for item in data["normalizer"]):
                raise TypeError("An item of key \"normalizer\" of TypedDict \"%s\" is not a str!" % (name))

        self.name = name
        self.field = "field" if "field" not in data else data["field"]
        self.types_strs = data["types"]
        self.types:dict[str,TypedDictTypeFilledTypedDict] = None
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = False if "print_all" not in data else data["print_all"]
        self.tags = {key: (value["tags"] if "tags" in value else []) for key, value in self.types_strs.items()}

        self.links_to_other_intermediates:list[Intermediate] = []
        self.parents:list[Intermediate] = []
        self.normalizers:list[NormalizerFunctionIntermediate]|None = None
        self.types_final:dict[tuple[str,type],ComparerSection.ComparerSection|None] = None
        self.check_types_final:dict[str,tuple[list[type],ComparerIntermediate|None]] = {}
        self.final:DictComparerSection.DictComparerSection = None

        self.children_has_normalizer = False

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
                type_intermediate:TypeAliasIntermediate = self.choose_intermediate(type_str, TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, choose_comparer_keys)
                self.links_to_other_intermediates.append(type_intermediate)
                type_intermediate.parents.append(self)
                types.append(type_intermediate)
        return types

    def set_comparer(self, key:str, data:TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate]) -> ComparerIntermediate|None:
        if "comparer" not in data or data["comparer"] is None: return None
        comparer:ComparerIntermediate|GroupIntermediate = self.choose_intermediate(data["comparer"], ComparerIntermediate|GroupIntermediate, "a Comparer or Group", intermediate_comparers, ["types", key, "comparer"])
        self.links_to_other_intermediates.append(comparer)
        comparer.parents.append(self)
        return comparer

    def set(self, intermediate_comparers:dict[str,Intermediate], functions:dict[str,Callable]) -> None:
        self.types = {}
        for key, data in self.types_strs.items():
            self.types[key] = {
                "comparer": self.set_comparer(key, data, intermediate_comparers),
                "type": self.choose_types(key, data, intermediate_comparers),
            }
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerFunctionIntermediate] = [self.choose_intermediate(normalizer_str, NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_intermediates.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)

    def create_final(self) -> None:
        self.types_final = {}
        normalizer_final = None if self.normalizers is None else [normalizer.final for normalizer in self.normalizers]
        self.final = TypedDictComparerSection.TypedDictComparerSection(
            name=self.field,
            types=self.types_final,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
        )

    def expand_types(self, types:Iterable[type|TypeAliasIntermediate]) -> Generator[type,None,None]:
        for item in types:
            if isinstance(item, type): yield item
            else: yield from item.types

    def link_finals(self) -> None:
        for types_key, types_value in self.types.items():
            comparer = types_value["comparer"]
            if isinstance(comparer, GroupIntermediate):
                for group_type, group_comparer_section in comparer.final.items():
                    self.types_final[types_key, group_type] = group_comparer_section
                self.check_types_final[types_key] = (list(self.expand_types(types_value["type"])), comparer)
            else:
                key_types = list(self.expand_types(types_value["type"]))
                comparer_final = (comparer.final if comparer is not None else None)
                for key_type in key_types:
                    self.types_final[types_key, key_type] = comparer_final
                self.check_types_final[types_key] = (list(self.expand_types(types_value["type"])), comparer)

    def check(self) -> None:
        self.final.check_initialization_parameters()
        for key, (key_types, comparer) in self.check_types_final.items():
            if comparer is None:
                for type_item in key_types:
                    if type_item in REQUIRES_COMPARER_TYPES:
                        raise TypeError("Key \"%s\" of TypedDictComparer \"%s\" accepts type %s, but has a null comparer!" % (key, self.name, type_item.__name__))
            else:
                if set(key_types) != set(comparer.my_type):
                    my_types = ", ".join(type_item.__name__ for type_item in sorted(key_types, key=lambda x: x.__name__))
                    its_types = ", ".join(type_item.__name__ for type_item in sorted(comparer.my_type, key=lambda x: x.__name__))
                    raise TypeError("Key \"%s\" of TypedDictComparer \"%s\" accepts types [%s], but its comparer, \"%s\", only accepts type [%s]!" % (key, self.name, my_types, comparer.name, its_types))

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
        GroupIntermediate: [],
        DictComparerIntermediate: [],
        ListComparerIntermediate: [],
        MainIntermediate: [],
        NormalizerFunctionIntermediate: [],
        TypeAliasIntermediate: [],
        TypedDictIntermediate: [],
    }
    for intermediate in intermediate_comparers:
        intermediate_types[type(intermediate)].append(intermediate)
    for intermediates in intermediate_types.values():
        yield from intermediates

def create_intermediates(name:str, data:ComparerType) -> tuple[list[tuple[str,MainIntermediate]], dict[str,Intermediate]]:
    '''Returns a list of MainIntermediates and a dict of all Intermediates.'''
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
            case "NormalizerFunction":
                intermediate_comparers[comparer_name] = NormalizerFunctionIntermediate(comparer_data, comparer_name, index)
            case "TypeAlias":
                intermediate_comparers[comparer_name] = TypeAliasIntermediate(comparer_data, comparer_name, index)
            case "TypedDict":
                intermediate_comparers[comparer_name] = TypedDictIntermediate(comparer_data, comparer_name, index)
            case _:
                raise ValueError("Comparer \"%s\" has an invalid \"type\" key: %s" % (comparer_name, comparer_data["type"]))
    return main_comparers, intermediate_comparers

def set_comparers(intermediate_comparers:dict[str,Intermediate], do_not_set_intermediates:set[str], functions:dict[str,Callable]) -> None:
    for comparer_name, comparer_intermediate in intermediate_comparers.items():
        if comparer_name in do_not_set_intermediates:
            continue
        comparer_intermediate.set(intermediate_comparers, functions)

def do_imports(main_comparer:MainIntermediate, partially_imported:set[str]) -> dict[str,Intermediate]:
    if main_comparer.imports is None: return {}
    all_intermediates:dict[str,tuple[Intermediate,str]] = {}
    for imported_comparer in main_comparer.imports:
        import_from = imported_comparer["from"]
        imported_intermediates = import_comparer(import_from, ComparerFunctions.functions, partially_imported)
        # check for circular import
        if import_from in partially_imported:
            raise RuntimeError("Circular import: %s" % partially_imported)

        for component in imported_comparer["components"]:
            # check for existence
            if component["component"] not in imported_intermediates:
                raise KeyError("Attempted to import component \"%s\" from \"%s\", which does not exist!" % (component["component"], import_from))
            intermediate = imported_intermediates[component["component"]]
            # set the name
            if "as" in component:
                intermediate.name = component["as"]
                name = component["as"]
            else:
                name = component["component"]
            # checking for name duplication
            if name in all_intermediates:
                duplicated_library = all_intermediates[name][1]
                raise RuntimeError("Attempted to import comparers with the same name, \"%s\" and \"%s\"!" % (duplicated_library, import_from))
            all_intermediates[name] = (intermediate, import_from)
    output = {name: intermediate for name, (intermediate, library) in all_intermediates.items()}
    return output

def propagate_comparer_variables(intermediate_comparers:dict[str,Intermediate]) -> None:
    for comparer_intermediate in intermediate_comparers.values():
        comparer_intermediate.propagate_variables()

def create_final_comparers(intermediate_comparers:dict[str,Intermediate]) -> None:
    for comparer_intermediate in intermediate_comparers.values():
        comparer_intermediate.create_final()

def link_final_comparers(intermediate_comparers:dict[str,Intermediate]) -> None:
    for comparer_intermediate in get_link_final_order(intermediate_comparers.values()):
        comparer_intermediate.link_finals()

def check_comparers(intermediate_comparers:dict[str,Intermediate]) -> None:
    for comparer_intermediate in intermediate_comparers.values():
        comparer_intermediate.check()

def parse_comparer_file(name:str, data:ComparerType, functions:dict[str,Callable]) -> Comparer.Comparer:
    if not isinstance(data, dict):
        raise TypeError("Comparer file \"%s\" is not a dict!" % (name))
    
    main_comparers, intermediate_comparers = create_intermediates(name, data)
    if len(main_comparers) == 0:
        raise ValueError("There is not a Main comparer in Comparer file \"%s\"!" % name)
    if len(main_comparers) > 1:
        raise ValueError("There are more than one Main comparer in Comparer file \"%s\": [%s]" % (", ".join(comparer_name for comparer_name, comparer_intermediate in main_comparers)))
    main_comparer = main_comparers[0][1]

    imported_intermediates = do_imports(main_comparer, set())
    for imported_intermediate in imported_intermediates:
        if imported_intermediate in intermediate_comparers:
            raise KeyError("Duplicate key \"%s\" between \"%s\" and an imported comparer!" % (imported_intermediate, name))
    intermediate_comparers.update(imported_intermediates)
    
    set_comparers(intermediate_comparers, imported_intermediates.keys(), functions)
    used_intermediates = get_used_intermediates(main_comparer)
    unused_intermediates = [intermediate for intermediate in intermediate_comparers.values() if intermediate not in used_intermediates]
    if len(unused_intermediates) > 0:
        print("Warning: Comparer file \"%s\" has %i unused comparers: %s" % (name, len(unused_intermediates), [intermediate.name for intermediate in unused_intermediates]))

    propagate_comparer_variables(intermediate_comparers)
    create_final_comparers(intermediate_comparers)
    link_final_comparers(intermediate_comparers)
    check_comparers(intermediate_comparers)

    return main_comparer.final

def parse_comparer_file_for_import(name:str, data:ComparerType, functions:dict[str,Callable], partially_imported:set[str]) -> dict[str,Intermediate]:
    if not isinstance(data, dict):
        raise TypeError("Comparer file \"%s\" is not a dict!" % (name))
    main_comparers, intermediate_comparers = create_intermediates(name, data)
    if len(main_comparers) == 0:
        raise ValueError("There is not a Main comparer in Comparer file \"%s\"!" % name)
    if len(main_comparers) > 1:
        raise ValueError("There are more than one Main comparer in Comparer file \"%s\": [%s]" % (", ".join(comparer_name for comparer_name, comparer_intermediate in main_comparers)))
    main_comparer = main_comparers[0][1]
    partially_imported.add(name)
    imported_intermediates = do_imports(main_comparer, partially_imported)
    for imported_intermediate in imported_intermediates:
        if imported_intermediate in intermediate_comparers:
            raise KeyError("Duplicate key \"%s\" between \"%s\" and an imported comparer!" % (imported_intermediate, name))
    intermediate_comparers.update(imported_intermediates)

    set_comparers(intermediate_comparers, imported_intermediates.keys(), functions)
    propagate_comparer_variables(intermediate_comparers)
    partially_imported.remove(name)
    return intermediate_comparers

def import_comparer(name:str, functions:dict[str,Callable], partially_imported:set[str]) -> dict[str,Intermediate]:
    if not isinstance(name, str):
        raise TypeError("`name` is not a str!")
    data = get_file(name)
    return parse_comparer_file_for_import(name, data, functions, partially_imported)

def load(name:str, functions:dict[str,Callable]) -> Comparer.Comparer:
    if not isinstance(name, str):
        raise TypeError("`name` is not a str!")
    data = get_file(name)
    return parse_comparer_file(name, data, functions)

def load_from_file(name:str, functions:dict[str,Callable]) -> WaitValue[Comparer.Comparer]:
    return WaitValue(FunctionCaller(load, args=[name, functions]))

def open_index_file() -> dict[str,dict]:
    with open(FileManager.COMPARERS_FILE, "rt") as f:
        return json.load(f)

def parse_comparers_index() -> dict[str,WaitValue[Comparer.Comparer]]:
    index = open_index_file()
    for comparer_file_name in index:
        comparer_file_path = FileManager.get_comparer_path(comparer_file_name)
        if not comparer_file_path.exists():
            raise FileNotFoundError("Comparer file \"%s\" is referred to by comparers.json, but does not exist!" % (comparer_file_name))
    return {comparer_file_name: load_from_file(comparer_file_name, ComparerFunctions.functions) for comparer_file_name in index}

comparers = parse_comparers_index()
