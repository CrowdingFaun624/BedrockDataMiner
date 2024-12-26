import traceback
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, cast

import pyjson5 as json

import Component.Accessor.AccessorTypeImporterEnvironment as AccessorTypeImporterEnvironment
import Component.Component as Component
import Component.ComponentFunctions as ComponentFunctions
import Component.ComponentTypes as ComponentTypes
import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.DataMinerImporterEnvironment as DataMinerImporterEnvironment
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Serializer.SerializerImporterEnvironment as SerializerImporterEnvironment
import Component.Structure.StructureImporterEnvironment as StructureImporterEnvironment
import Component.Structure.StructureTagImporterEnvironment as StructureTagImporterEnvironment
import Component.Tablifier.TablifierImporterEnvironment as TablifierImporterEnvironment
import Component.Version.VersionFileTypeImporterEnvironment as VersionFileTypeImporterEnvironment
import Component.Version.VersionImporterEnvironment as VersionImporterEnvironment
import Component.VersionTag.LatestSlotImporterEnvironment as LatestSlotImporterEnvironment
import Component.VersionTag.VersionTagImporterEnvironment as VersionTagImporterEnvironment
import Component.VersionTag.VersionTagOrderImporterEnvironment as VersionTagOrderImporterEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import DataMiner.DataMinerCollection as DataMinerCollection
    import Downloader.AccessorType as AccessorType
    import Serializer.Serializer as Serializer
    import Structure.StructureBase as StructureBase
    import Structure.StructureTag as StructureTag
    import Tablifier.Tablifier as Tablifier
    import Version.Version as Version
    import Version.VersionFileType as VersionFileType
    import Version.VersionTag.VersionTag as VersionTag
    import Version.VersionTag.VersionTagOrder as VersionTagOrder

importer_environment_types:list[type[ImporterEnvironment.ImporterEnvironment]] = [
    AccessorTypeImporterEnvironment.AccessorTypeImporterEnvironment,
    DataMinerImporterEnvironment.DataMinerImporterEnvironment,
    LatestSlotImporterEnvironment.LatestSlotImporterEnvironment,
    SerializerImporterEnvironment.SerializerImporterEnvironment,
    StructureImporterEnvironment.StructureImporterEnvironment,
    StructureTagImporterEnvironment.StructureTagImporterEnvironment,
    TablifierImporterEnvironment.TablifierImporterEnvironment,
    VersionFileTypeImporterEnvironment.VersionFileTypeImporterEnvironment,
    VersionImporterEnvironment.VersionImporterEnvironment,
    VersionTagImporterEnvironment.VersionTagImporterEnvironment,
    VersionTagOrderImporterEnvironment.VersionTagOrderImporterEnvironment,
]

component_types_dict:dict[str,type[Component.Component]] = {component_type.class_name: component_type for component_type in ComponentTypes.component_types}

component_group_type_verifier = TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    loose=True
), "a dict", "a str", "a dict")

def create_inline_component(component_data:ComponentTyping.ComponentTypedDicts, parent_component:Component.Component, assume_type:str|None) -> Component.Component:
    component_name = parent_component.get_inline_component_name()
    component_type_str = component_data.get("type", assume_type)
    if component_type_str is None:
        raise Exceptions.ComponentTypeMissingError(component_name, parent_component.component_group)
    component_type = component_types_dict.get(component_type_str)
    if component_type is None:
        raise Exceptions.UnrecognizedComponentTypeError(component_type_str, "%s in %s" % (component_name, parent_component.component_group), "(Must be one of [%s])" % (", ".join(component.class_name for component in ComponentTypes.component_types),))
    component = component_type(component_data, component_name, parent_component.component_group, None)
    component.inline_parent = parent_component
    return component

def create_components(name:str, data:ComponentTyping.ComponentGroupFileType, importer_environment:ImporterEnvironment.ImporterEnvironment) -> dict[str,Component.Component]:
    '''Returns a dict of all Components in the Component group.'''
    components:dict[str,Component.Component] = {}
    for index, (component_name, component_data) in enumerate(data.items()):
        component_type_str = component_data.get("type", importer_environment.assume_type)
        if component_type_str is None:
            raise Exceptions.ComponentTypeMissingError(component_name, name)
        component_type = component_types_dict.get(component_type_str)
        if component_type is None:
            raise Exceptions.UnrecognizedComponentTypeError(component_type_str, "%s in %s" % (component_name, name), "(Must be one of [%s])" % (", ".join(component.class_name for component in ComponentTypes.component_types),))
        component = component_type(component_data, component_name, name, index)
        components[component_name] = component
    return components

def get_file(path:Path) -> ComponentTyping.ComponentGroupFileType:
    with open(path, "rt") as f:
        return json.decode_io(f) # type: ignore[reportArgumentType] # stupid types are almost the same but not quite

def propagate_variables(all_components:dict[str,dict[str,Component.Component]]) -> None:
    all_components_flat:list[Component.Component] = []
    all_components_flat_memo:set[Component.Component] = set()
    for components in all_components.values():
        for component in components.values():
            all_components_flat.extend(component.get_all_descendants(all_components_flat_memo))
    components_queue = deque(all_components_flat) # components_queue and unvisited_components should mirror each other
    unvisited_components = all_components_flat_memo # the set of Components that need to be updated or re-updated.
    while len(components_queue) > 0:
        component = components_queue.popleft()
        unvisited_components.remove(component)
        component_has_changed = component.propagate_variables()
        if component_has_changed:
            for parent_component in component.parents:
                if parent_component not in unvisited_components:
                    unvisited_components.add(parent_component)
                    components_queue.append(parent_component)

def create_all_components() -> tuple[dict[str,dict[str,Component.Component]], dict[str,ImporterEnvironment.ImporterEnvironment]]:
    all_components:dict[str,dict[str,Component.Component]] = {}
    already_paths:dict[Path,ImporterEnvironment.ImporterEnvironment] = {}
    importer_environments:dict[str,ImporterEnvironment.ImporterEnvironment] = {}
    for importer_environment_type in importer_environment_types:
        importer_environment = importer_environment_type()
        for file_path in importer_environment.get_component_files():
            name = importer_environment.get_component_group_name(file_path)
            if file_path in already_paths:
                raise Exceptions.ImporterEnvironmentPathCollisionError(file_path, importer_environment, already_paths[file_path])
            if name in importer_environments:
                raise Exceptions.ImporterEnvironmentNameCollisionError(name, importer_environment, importer_environments[name])
            importer_environments[name] = importer_environment
            already_paths[file_path] = importer_environment
            components_data = get_file(file_path)
            if importer_environment.single_component:
                components_data = cast(ComponentTyping.ComponentGroupFileType, {"": components_data})
            component_group_type_verifier.base_verify(components_data, [name])
            all_components[name] = create_components(name, components_data, importer_environment)
    return all_components, importer_environments

def get_imports(all_components:dict[str,dict[str,Component.Component]], importer_environments:dict[str,ImporterEnvironment.ImporterEnvironment]) -> dict[str,dict[str,dict[str,Component.Component]]]:
    return {
        name: importer_environments[name].get_imports(components, all_components, name)
        for name, components in all_components.items()
    }

def set_components(all_components:dict[str,dict[str,Component.Component]], component_imports:dict[str,dict[str,dict[str,Component.Component]]], functions:dict[str,Callable]) -> None:
    for name, components in all_components.items():
        for component in components.values():
            component.set_component(components, component_imports[name], functions, create_inline_component)

def create_finals(all_components:dict[str,dict[str,Component.Component]]) -> None:
    for components in all_components.values():
        for component in components.values():
            component.create_final()

def link_finals(all_components:dict[str,dict[str,Component.Component]]) -> list[Exception]:
    exceptions:list[Exception] = []
    for components in all_components.values():
        for component in components.values():
            exceptions.extend(component.link_finals())
    if len(exceptions) > 0:
        for exception in exceptions:
            traceback.print_exception(exception)
        raise Exceptions.ComponentParseError()
    return exceptions

def check_components(all_components:dict[str,dict[str,Component.Component]]) -> None:
    exceptions:list[Exception] = []
    for components in all_components.values():
        for component in components.values():
            exceptions.extend(component.check())
    if len(exceptions) > 0:
        for exception in exceptions:
            traceback.print_exception(exception)
        raise Exceptions.ComponentParseError()

def finalize_components(all_components:dict[str,dict[str,Component.Component]]) -> None:
    for components in all_components.values():
        for component in components.values():
            component.finalize()

def get_outputs(all_components:dict[str,dict[str,Component.Component]], importer_environments:dict[str,ImporterEnvironment.ImporterEnvironment]) -> dict[str,Any]:
    return {name: importer_environments[name].get_output(components, name) for name, components in all_components.items()}

def check_for_unused_components(all_components:dict[str,dict[str,Component.Component]], importer_environments:dict[str,ImporterEnvironment.ImporterEnvironment]) -> None:
    visited_nodes:set[Component.Component] = set()
    unvisited_nodes:list[Component.Component] = []
    for name, components in all_components.items():
        unvisited_nodes.extend(importer_environments[name].get_assumed_used_components(components, name))
    while len(unvisited_nodes) > 0:
        unvisited_node = unvisited_nodes.pop()
        if unvisited_node in visited_nodes: continue
        unvisited_nodes.extend(
            neighbor
            for neighbor in unvisited_node.links_to_other_components
            if neighbor not in visited_nodes
        )
        visited_nodes.add(unvisited_node)
    unused_components:list[Component.Component] = []
    for components in all_components.values():
        unused_components.extend(component for component in components.values() if component not in visited_nodes)
    for unused_component in unused_components:
        print("Warning: Unused component: %r" % (unused_component,))

def finalize_importer_environments(output:dict[str,Any], importer_environments:dict[str,ImporterEnvironment.ImporterEnvironment]) -> None:
    for name, component_group_output in output.items():
        importer_environments[name].finalize(component_group_output, output)

def check_importer_environments(output:dict[str,Any], importer_environments:dict[str,ImporterEnvironment.ImporterEnvironment]) -> None:
    exceptions:list[Exception] = []
    for name, component_group_output in output.items():
        exceptions.extend(importer_environments[name].check(component_group_output, output))
    if len(exceptions) > 0:
        for exception in exceptions:
            traceback.print_exception(exception)
        raise Exceptions.ComponentParseError()

def get_all_functions() -> dict[str,Callable]:
    functions:dict[str,Callable] = {}
    functions.update(ComponentFunctions.functions)
    functions.update((name, script) for name, script in Scripts.scripts.scripts.items() if callable(script.object))
    return functions

def parse_all_component_groups() -> dict[str,Any]:
    functions = get_all_functions()
    all_components, importer_environments = create_all_components()
    component_imports = get_imports(all_components, importer_environments)
    set_components(all_components, component_imports, functions)
    propagate_variables(all_components)
    create_finals(all_components)
    link_finals(all_components)
    check_components(all_components)
    finalize_components(all_components)
    output = get_outputs(all_components, importer_environments)
    check_for_unused_components(all_components, importer_environments)
    finalize_importer_environments(output, importer_environments)
    check_importer_environments(output, importer_environments)
    return output

all_component_groups = parse_all_component_groups()

accessor_types:dict[str,"AccessorType.AccessorType"] = all_component_groups["accessor_types"]
dataminer_collections:dict[str,"DataMinerCollection.DataMinerCollection"] = all_component_groups["dataminer_collections"]
latest_slots:list[str] = all_component_groups["latest_slots"]
serializers:dict[str,"Serializer.Serializer"] = all_component_groups["serializers"]
structures:dict[str,"StructureBase.StructureBase"] = {component_group_name: component_group for component_group_name, component_group in all_component_groups.items() if component_group_name.startswith("structure/")}
structure_tags:dict[str,"StructureTag.StructureTag"] = all_component_groups["structure_tags"]
tablifiers:dict[str,"Tablifier.Tablifier"] = all_component_groups["tablifiers"]
version_file_types:dict[str,"VersionFileType.VersionFileType"] = all_component_groups["version_file_types"]
version_tags_order:"VersionTagOrder.VersionTagOrder" = all_component_groups["version_tags_order"]
version_tags:dict[str,"VersionTag.VersionTag"] = all_component_groups["version_tags"]
versions:dict[str,"Version.Version"] = all_component_groups["versions"]
