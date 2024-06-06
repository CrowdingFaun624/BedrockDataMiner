import json
import traceback

import Structure.Importer.BaseComponent as BaseComponent
import Structure.Importer.CacheComponent as CacheComponent
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.DictComponent as DictComponent
import Structure.Importer.GroupComponent as GroupComponent
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
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

component_types:list[type[Component.Component]] = [
    CacheComponent.CacheComponent,
    DictComponent.DictComponent,
    GroupComponent.GroupComponent,
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
    NormalizerComponent.NormalizerComponent,
    TagComponent.TagComponent,
]

structure_file_type_verifier = TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
    loose=True
), "a dict", "a str", "a dict")

def get_unused_components(base_component:BaseComponent.BaseComponent, components:dict[str,Component.Component]) -> list[Component.Component]:
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
    output:list[Component.Component] = []
    for component in components.values():
        if component not in visited_nodes: output.append(component)
    return output

def create_components(name:str, data:ComponentTyping.StructureFileType) -> dict[str,Component.Component]:
    '''Returns a list of BaseComponents and a dict of all Components.'''
    components:dict[str,Component.Component] = {}
    for component_name, component_data in data.items():
        for component_type in component_types:
            if component_type.class_name == component_data["type"]:
                component = component_type(component_data, component_name) # type:ignore All subclasses have this sort of __init__.
                components[component_name] = component
                break
        else:
            raise Exceptions.UnrecognizedComponentTypeError(component_data["type"], component_name, "(Must be one of [%s])" % (", ".join(component_type.class_name for component_Type in component_types),))
    return components

def do_imports(all_components:dict[str,dict[str,Component.Component]]) -> dict[str,dict[str,dict[str,Component.Component]]]:
    output:dict[str,dict[str,dict[str,Component.Component]]] = {}
    for structure_name, components in all_components.items():
        output[structure_name] = {}
        imports:list[ComponentTyping.ImportTypedDict]|None = None
        for component in components.values():
            if isinstance(component, BaseComponent.BaseComponent):
                imports = component.imports
                break
        if imports is None: continue
        for import_data in imports:
            import_from = import_data["from"]
            if import_from == structure_name:
                raise Exceptions.ComponentImporterCircularImportError([structure_name], "(attempted to self-import)")
            output[structure_name][import_from] = {}
            for import_component_data in import_data["components"]:
                import_component_name = import_component_data["component"]
                import_component_as = import_component_data.get("as", import_component_name)
                output[structure_name][import_from][import_component_as] = all_components[import_from][import_component_name]
    return output

def get_file(name:str) -> ComponentTyping.StructureFileType:
    with open(FileManager.ASSETS_DIRECTORY.joinpath(name + ".json"), "rt") as f:
        return json.load(f)

def parse_all_structures() -> dict[str,StructureBase.StructureBase]:
    functions = StructureFunctions.functions
    all_components:dict[str,dict[str,Component.Component]] = {}
    for structure_file in FileManager.STRUCTURES_DIRECTORY.iterdir():
        name = "structures/" + structure_file.stem
        components_data = get_file(name)
        structure_file_type_verifier.base_verify(components_data)
        all_components[name] = create_components(name, components_data)

    component_imports = do_imports(all_components)
    for name, components in all_components.items():
        for component in components.values(): component.set_component(components, component_imports[name], functions)
    for name, components in all_components.items():
        for component in components.values(): component.propagate_variables()
    for name, components in all_components.items():
        for component in components.values(): component.create_final()
    for name, components in all_components.items():
        for component in components.values(): component.link_finals()
    exceptions:list[Exception] = []
    for name, components, in all_components.items():
        for component in components.values(): exceptions.extend(component.check())
    if len(exceptions) > 0:
        for exception in exceptions:
            traceback.print_exception(exception)
        raise Exceptions.ComponentParseError()
    for name, components in all_components.items():
        for component in components.values(): component.finalize()

    output:dict[str,StructureBase.StructureBase] = {}
    for name, components in all_components.items():
        base_components:dict[str,BaseComponent.BaseComponent] = {}
        for component_name, component in components.items():
            if isinstance(component, BaseComponent.BaseComponent):
                base_components[component_name] = component
        if len(base_components) != 1:
            raise Exceptions.BaseComponentCountError(name, len(base_components), "(names: [%s])" % (", ".join(base_components.keys()),))
        base_component = list(base_components.values())[0]
        unused_components = get_unused_components(base_component, components)
        for unused_component in unused_components:
            print("Warning: Unused %r in %s." % (unused_component, name))
        output[name] = base_component.get_final()
    return output

structures = parse_all_structures()
