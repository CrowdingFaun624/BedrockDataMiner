import json
import traceback
from typing import Callable, Generator, Iterable

import Structure.Importer.BaseComponent as BaseComponent
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.DictComponent as DictComponent
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.KeymapComponent as KeymapComponent
import Structure.Importer.ListComponent as ListComponent
import Structure.Importer.NbtBaseComponent as NbtBaseComponent
import Structure.Importer.NbtTagComponent as NbtTagComponent
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.TagComponent as TagComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.Importer.VolumeComponent as VolumeComponent
import Structure.StructureBase as StructureBase
import Structure.StructureFunctions as StructureFunctions
import Utilities.FileManager as FileManager

component_types:list[type[Component.Component]] = [
    GroupComponent.GroupComponent, # near the top so they are created first
    NormalizerComponent.NormalizerComponent,
    TagComponent.TagComponent,
    DictComponent.DictComponent,
    ListComponent.ListComponent,
    BaseComponent.BaseComponent,
    TypeAliasComponent.TypeAliasComponent,
    KeymapComponent.KeymapComponent,
    VolumeComponent.VolumeComponent,
    NbtBaseComponent.NbtBaseComponent,
    NbtTagComponent.NbtTagByteArrayComponent,
    NbtTagComponent.NbtTagCompoundComponent,
    NbtTagComponent.NbtTagIntArrayComponent,
    NbtTagComponent.NbtTagListComponent,
    NbtTagComponent.NbtTagLongArrayComponent,
    NbtTagComponent.NbtKeymapTagCompoundComponent,
]

def get_file(name:str) -> ComponentTyping.StructureFileType:
    with open(FileManager.get_structure_path(name), "rt") as f:
        return json.load(f)

def get_used_components(base_component:BaseComponent.BaseComponent) -> set[Component.Component]:
    visited_nodes:set[Component.Component] = set()
    unvisited_nodes:list[Component.Component] = [base_component]
    while len(unvisited_nodes) > 0:
        unvisited_node = unvisited_nodes.pop()
        if unvisited_node in visited_nodes: continue
        for neighbor in unvisited_node.links_to_other_components:
            if neighbor in visited_nodes:
                continue
            else:
                unvisited_nodes.append(neighbor)
        visited_nodes.add(unvisited_node)
    return visited_nodes

def get_link_final_order(components:Iterable[tuple[str,Component.Component]]) -> Generator[tuple[str,Component.Component], None, None]:
    component_usages:dict[type[Component.Component], list[tuple[str,Component.Component]]] = {component_type: [] for component_type in component_types}
    for component_name, component in components:
        component_usages[type(component)].append((component_name, component))
    for used_components in component_usages.values():
        yield from used_components

def create_components(name:str, data:ComponentTyping.StructureFileType) -> tuple[list[tuple[str,BaseComponent.BaseComponent]], dict[str,Component.Component]]:
    '''Returns a list of BaseComponents and a dict of all Components.'''
    components:dict[str,Component.Component] = {}
    base_components:list[tuple[str,BaseComponent.BaseComponent]] = []
    for index, (component_name, component_data) in enumerate(data.items()):
        if not isinstance(component_name, str):
            raise TypeError("Component index %i's name is not a str!" % (index))
        if not isinstance(component_data, dict):
            raise TypeError("Component \"%s\" is not a dict!" % (component_name))
        if "type" not in component_data:
            raise KeyError("Component \"%s\" has no \"type\" key!" % (component_name))
        if not isinstance(component_data["type"], str):
            raise TypeError("Key \"type\" of Component \"%s\" is not a str!" % (component_name))
        for component_type in component_types:
            if component_type.class_name == component_data["type"]:
                component = component_type(component_data, component_name, index)
                components[component_name] = component
                if component_type is BaseComponent.BaseComponent:
                    assert isinstance(component, BaseComponent.BaseComponent)
                    base_components.append((component_name, component))
                break
        else:
            raise ValueError("Component \"%s\" has an invalid \"type\" key: %s. Must be one of [%s]!" % (component_name, component_data["type"], ", ".join(component_type.class_name for component_type in component_types)))

    return base_components, components

def set_components(components:dict[str,Component.Component], exclude:set[str], functions:dict[str,Callable]) -> None:
    for component_name, component in components.items():
        if component_name in exclude:
            continue
        component.set_component(components, functions)

def do_imports(base_components:BaseComponent.BaseComponent, partially_imported:set[str], config:ImporterConfig.ImporterConfig) -> dict[str,Component.Component]:
    if base_components.imports is None: return {}
    all_components:dict[str,tuple[Component.Component,str]] = {}
    if not config.allow_imports and len(base_components.imports) > 0:
        raise ValueError("Base %s attempted to import in an environment where imports are not allowed!" % (base_components,))
    for imported_structure_data in base_components.imports:
        import_from = imported_structure_data["from"]
        imported_components = import_component(import_from, StructureFunctions.functions, partially_imported, config)
        # check for circular import
        if import_from in partially_imported:
            raise RuntimeError("Circular import: %s" % partially_imported)

        for imported_component_data in imported_structure_data["components"]:
            # check for existence
            if imported_component_data["component"] not in imported_components:
                raise KeyError("Attempted to import Component \"%s\" from \"%s\", which does not exist!" % (imported_component_data["component"], import_from))
            component = imported_components[imported_component_data["component"]]
            # set the name
            if "as" in imported_component_data:
                component.name = imported_component_data["as"]
                name = imported_component_data["as"]
            else:
                name = imported_component_data["component"]
            # checking for name duplication
            if name in all_components:
                duplicated_structure = all_components[name][1]
                raise RuntimeError("Attempted to import Components with the same name, \"%s\" and \"%s\"!" % (duplicated_structure, import_from))
            all_components[name] = (component, import_from)
    output = {name: component for name, (component, structure_from) in all_components.items()}
    return output

def propagate_component_variables(components:dict[str,Component.Component]) -> None:
    for component in components.values():
        component.propagate_variables()

def create_final_components(components:dict[str,Component.Component], exclude:set[str]) -> None:
    for component_name, component in components.items():
        if component_name in exclude: continue
        component.create_final()

def link_final_components(components:dict[str,Component.Component], exclude:set[str]) -> None:
    for component_name, component in get_link_final_order(components.items()):
        if component_name in exclude: continue
        component.link_finals()

def check_components(components:dict[str,Component.Component], config:ImporterConfig.ImporterConfig, exclude:set[str]) -> None:
    exceptions:list[Exception] = []
    for component_name, component in components.items():
        if component_name in exclude: continue
        new_exceptions = component.check(config)
        if new_exceptions is not None:
            exceptions.extend(new_exceptions)
    for exception in exceptions:
        traceback.print_exception(exception)
        print()
    if len(exceptions) > 0:
        raise RuntimeError("Failed to parse structure!")

def finalize_finals(components:dict[str,Component.Component], exclude:set[str]) -> None:
    for component_name, component in components.items():
        if component_name in exclude: continue
        component.finalize_finals()

def parse_structure_file(name:str, data:ComponentTyping.StructureFileType, functions:dict[str,Callable], config:ImporterConfig.ImporterConfig=ImporterConfig.DEFAULT) -> StructureBase.StructureBase:
    if not isinstance(data, dict):
        raise TypeError("Structure file \"%s\" is not a dict!" % (name))

    base_components, components = create_components(name, data)
    if len(base_components) == 0:
        raise ValueError("There is not a BaseComponent in Structure file \"%s\"!" % name)
    if len(base_components) > 1:
        raise ValueError("There are more than one BaseComponents in Structure file \"%s\": [%s]" % (", ".join(component_name for component_name, component in base_components)))
    base_component = base_components[0][1]

    imported_components = do_imports(base_component, set(), config)
    for imported_component in imported_components:
        if imported_component in components:
            raise KeyError("Duplicate key \"%s\" between \"%s\" and an imported Component!" % (imported_component, name))
    components.update(imported_components)

    set_components(components, set(imported_components.keys()), functions)
    used_components = get_used_components(base_component)
    unused_components = [component for component in components.values() if component not in used_components]
    if len(unused_components) > 0:
        print("Warning: Structure file \"%s\" has %i unused components: %s" % (name, len(unused_components), [component.name for component in unused_components]))

    propagate_component_variables(components)
    create_final_components(components, exclude=set(imported_components.keys()))
    link_final_components(components, exclude=set(imported_components.keys()))
    check_components(components, config, exclude=set(imported_components.keys()), )
    finalize_finals(components, exclude=set(imported_components.keys()))

    assert base_component.final is not None
    return base_component.final

def parse_structure_file_for_import(name:str, data:ComponentTyping.StructureFileType, functions:dict[str,Callable], partially_imported:set[str], config:ImporterConfig.ImporterConfig) -> dict[str,Component.Component]:
    if not isinstance(data, dict):
        raise TypeError("Structure file \"%s\" is not a dict!" % (name))
    base_components, components = create_components(name, data)
    if len(base_components) == 0:
        raise ValueError("There is not a BaseComponent in Structure file \"%s\"!" % name)
    if len(base_components) > 1:
        raise ValueError("There are more than one BaseComponent in Structure file \"%s\": [%s]" % (", ".join(component_name for component_name, component in base_components)))
    base_component = base_components[0][1]
    partially_imported.add(name)
    imported_components = do_imports(base_component, partially_imported, config)
    for imported_component in imported_components:
        if imported_component in components:
            raise KeyError("Duplicate key \"%s\" between \"%s\" and an imported component!" % (imported_component, name))
    components.update(imported_components)

    set_components(components, set(imported_components.keys()), functions)
    propagate_component_variables(components)
    create_final_components(components, exclude=set(imported_components.keys()))
    link_final_components(components, exclude=set(imported_components.keys()))
    check_components(components, config, exclude=set(imported_components.keys()))
    finalize_finals(components, exclude=set(imported_components.keys()))
    partially_imported.remove(name)
    return components

def import_component(name:str, functions:dict[str,Callable], partially_imported:set[str], config:ImporterConfig.ImporterConfig) -> dict[str,Component.Component]:
    if not isinstance(name, str):
        raise TypeError("`name` is not a str!")
    data = get_file(name)
    return parse_structure_file_for_import(name, data, functions, partially_imported, config)

def load(name:str, functions:dict[str,Callable]) -> StructureBase.StructureBase:
    if not isinstance(name, str):
        raise TypeError("`name` is not a str!")
    data = get_file(name)
    return parse_structure_file(name, data, functions)

def load_from_file(name:str, functions:dict[str,Callable]) -> StructureBase.StructureBase:
    return load(name, functions)

def open_index_file() -> dict[str,dict]:
    with open(FileManager.STRUCTURES_FILE, "rt") as f:
        return json.load(f)

def parse_structures_index() -> dict[str,StructureBase.StructureBase]:
    index = open_index_file()
    for structure_file_name in index:
        structure_file_path = FileManager.get_structure_path(structure_file_name)
        if not structure_file_path.exists():
            raise FileNotFoundError("Structure file \"%s\" is referred to by structures.json, but does not exist!" % (structure_file_name))
    return {structure_file_name: load_from_file(structure_file_name, StructureFunctions.functions) for structure_file_name in index}

structures = parse_structures_index()
