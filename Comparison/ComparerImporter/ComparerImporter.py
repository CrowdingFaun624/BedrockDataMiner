import json
import traceback
from typing import Callable, Generator, Iterable

import Comparison.Comparer as Comparer
import Comparison.ComparerFunctions as ComparerFunctions
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.DictComparerIntermediate as DictComparerIntermediate
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.ListComparerIntermediate as ListComparerIntermediate
import Comparison.ComparerImporter.MainIntermediate as MainIntermediate
import Comparison.ComparerImporter.NbtBaseIntermediate as NbtBaseIntermediate
import Comparison.ComparerImporter.NbtTagCompoundComparerIntermediate as NbtTagCompoundComparerIntermediate
import Comparison.ComparerImporter.NbtTagListComparerIntermediate as NbtTagListComparerIntermediate
import Comparison.ComparerImporter.NbtTypedTagCompoundComparerIntermediate as NbtTypedTagCompoundComparerIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ComparerImporter.TypedDictComparerIntermediate as TypedDictComparerIntermediate
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller, WaitValue

comparer_types:list[type[Intermediate.Intermediate]] = [
    GroupIntermediate.GroupIntermediate, # near the top so they are created first
    NormalizerFunctionIntermediate.NormalizerFunctionIntermediate,
    DictComparerIntermediate.DictComparerIntermediate,
    ListComparerIntermediate.ListComparerIntermediate,
    MainIntermediate.MainIntermediate,
    TypeAliasIntermediate.TypeAliasIntermediate,
    TypedDictComparerIntermediate.TypedDictComparerIntermediate,
    NbtBaseIntermediate.NbtBaseIntermediate,
    NbtTagListComparerIntermediate.NbtTagByteArrayComparerIntermediate,
    NbtTagCompoundComparerIntermediate.NbtTagCompoundComparerIntermediate,
    NbtTagListComparerIntermediate.NbtTagIntArrayComparerIntermediate,
    NbtTagListComparerIntermediate.NbtTagListComparerIntermediate,
    NbtTagListComparerIntermediate.NbtTagLongArrayComparerIntermediate,
    NbtTypedTagCompoundComparerIntermediate.NbtTypedTagCompoundComparerIntermediate,
]

def get_file(name:str) -> ComparerTyping.ComparerType:
    with open(FileManager.get_comparer_path(name), "rt") as f:
        return json.load(f)

def get_used_intermediates(main_comparer:MainIntermediate.MainIntermediate) -> set[Intermediate.Intermediate]:
    visited_nodes:set[Intermediate.Intermediate] = set()
    unvisited_nodes:list[Intermediate.Intermediate] = [main_comparer]
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

def get_link_final_order(intermediate_comparers:Iterable[tuple[str,Intermediate.Intermediate]]) -> Generator[tuple[str,Intermediate.Intermediate], None, None]:
    intermediate_types:dict[type[Intermediate.Intermediate], list[tuple[str,Intermediate.Intermediate]]] = {comparer_type: [] for comparer_type in comparer_types}
    for name, intermediate in intermediate_comparers:
        intermediate_types[type(intermediate)].append((name, intermediate))
    for intermediates in intermediate_types.values():
        yield from intermediates

def create_intermediates(name:str, data:ComparerTyping.ComparerType) -> tuple[list[tuple[str,MainIntermediate.MainIntermediate]], dict[str,Intermediate.Intermediate]]:
    '''Returns a list of MainIntermediates and a dict of all Intermediates.'''
    intermediate_comparers:dict[str,Intermediate.Intermediate] = {}
    main_comparers:list[tuple[str,MainIntermediate.MainIntermediate]] = []
    for index, (comparer_name, comparer_data) in enumerate(data.items()):
        if not isinstance(comparer_name, str):
            raise TypeError("Comparer index %i's name is not a str!" % (index))
        if not isinstance(comparer_data, dict):
            raise TypeError("Comparer \"%s\" is not a dict!" % (comparer_name))
        if "type" not in comparer_data:
            raise KeyError("Comparer \"%s\" has no \"type\" key!" % (comparer_name))
        if not isinstance(comparer_data["type"], str):
            raise TypeError("Key \"type\" of Comparer \"%s\" is not a str!" % (comparer_name))
        for comparer_type in comparer_types:
            if comparer_type.class_name == comparer_data["type"]:
                intermediate_comparer = comparer_type(comparer_data, comparer_name, index)
                intermediate_comparers[comparer_name] = intermediate_comparer
                if comparer_type is MainIntermediate.MainIntermediate:
                    assert isinstance(intermediate_comparer, MainIntermediate.MainIntermediate) # >:(
                    main_comparers.append((comparer_name, intermediate_comparer))
                break
        else:
            raise ValueError("Comparer \"%s\" has an invalid \"type\" key: %s. Must be one of [%s]!" % (comparer_name, comparer_data["type"], ", ".join(comparer_type.class_name for comparer_type in comparer_types)))
                
    return main_comparers, intermediate_comparers

def set_comparers(intermediate_comparers:dict[str,Intermediate.Intermediate], do_not_set_intermediates:set[str], functions:dict[str,Callable]) -> None:
    for comparer_name, comparer_intermediate in intermediate_comparers.items():
        if comparer_name in do_not_set_intermediates:
            continue
        comparer_intermediate.set(intermediate_comparers, functions)

def do_imports(main_comparer:MainIntermediate.MainIntermediate, partially_imported:set[str]) -> dict[str,Intermediate.Intermediate]:
    if main_comparer.imports is None: return {}
    all_intermediates:dict[str,tuple[Intermediate.Intermediate,str]] = {}
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

def propagate_comparer_variables(intermediate_comparers:dict[str,Intermediate.Intermediate]) -> None:
    for comparer_intermediate in intermediate_comparers.values():
        comparer_intermediate.propagate_variables()

def create_final_comparers(intermediate_comparers:dict[str,Intermediate.Intermediate], exclude:set[str]) -> None:
    for name, comparer_intermediate in intermediate_comparers.items():
        if name in exclude: continue
        comparer_intermediate.create_final()

def link_final_comparers(intermediate_comparers:dict[str,Intermediate.Intermediate], exclude:set[str]) -> None:
    for name, comparer_intermediate in get_link_final_order(intermediate_comparers.items()):
        if name in exclude: continue
        comparer_intermediate.link_finals()

def check_comparers(intermediate_comparers:dict[str,Intermediate.Intermediate], exclude:set[str]) -> None:
    exceptions:list[Exception] = []
    for name, comparer_intermediate in intermediate_comparers.items():
        if name in exclude: continue
        new_exceptions = comparer_intermediate.check()
        if new_exceptions is not None:
            exceptions.extend(new_exceptions)
    for exception in exceptions:
        traceback.print_exception(exception)
        print()
    if len(exceptions) > 0:
        raise RuntimeError("Failed to parse comparer!")

def finalize_finals(intermediate_comparers:dict[str,Intermediate.Intermediate], exclude:set[str]) -> None:
    for name, comparer_intermediate in intermediate_comparers.items():
        if name in exclude: continue
        comparer_intermediate.finalize_finals()

def parse_comparer_file(name:str, data:ComparerTyping.ComparerType, functions:dict[str,Callable]) -> Comparer.Comparer:
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

    set_comparers(intermediate_comparers, set(imported_intermediates.keys()), functions)
    used_intermediates = get_used_intermediates(main_comparer)
    unused_intermediates = [intermediate for intermediate in intermediate_comparers.values() if intermediate not in used_intermediates]
    if len(unused_intermediates) > 0:
        print("Warning: Comparer file \"%s\" has %i unused comparers: %s" % (name, len(unused_intermediates), [intermediate.name for intermediate in unused_intermediates]))

    propagate_comparer_variables(intermediate_comparers)
    create_final_comparers(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    link_final_comparers(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    check_comparers(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    finalize_finals(intermediate_comparers, exclude=set(imported_intermediates.keys()))

    assert main_comparer.final is not None
    return main_comparer.final

def parse_comparer_file_for_import(name:str, data:ComparerTyping.ComparerType, functions:dict[str,Callable], partially_imported:set[str]) -> dict[str,Intermediate.Intermediate]:
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

    set_comparers(intermediate_comparers, set(imported_intermediates.keys()), functions)
    propagate_comparer_variables(intermediate_comparers)
    create_final_comparers(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    link_final_comparers(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    check_comparers(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    finalize_finals(intermediate_comparers, exclude=set(imported_intermediates.keys()))
    partially_imported.remove(name)
    return intermediate_comparers

def import_comparer(name:str, functions:dict[str,Callable], partially_imported:set[str]) -> dict[str,Intermediate.Intermediate]:
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
