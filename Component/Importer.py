from collections import deque
from pathlib import Path
from types import EllipsisType
from typing import Any, Iterable, Sequence, cast

import pyjson5 as json

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Accessor.AccessorTypeImporterEnvironment import (
    AccessorTypeImporterEnvironment,
)
from Component.Component import Component
from Component.ComponentTypes import component_types
from Component.ComponentTyping import (
    ComponentGroupFileType,
    ComponentTypedDicts,
    CreateComponentFunction,
)
from Component.Dataminer.DataminerImporterEnvironment import (
    DataminerImporterEnvironment,
)
from Component.ImporterEnvironment import ImporterEnvironment
from Component.Log.LogImporterEnvironment import LogImporterEnvironment
from Component.ScriptImporter import ScriptSetSetSet
from Component.Serializer.SerializerImporterEnvironment import (
    SerializerImporterEnvironment,
)
from Component.Structure.StructureImporterEnvironment import (
    StructureImporterEnvironment,
)
from Component.Structure.StructureTagImporterEnvironment import (
    StructureTagImporterEnvironment,
)
from Component.Tablifier.TablifierImporterEnvironment import (
    TablifierImporterEnvironment,
)
from Component.Version.VersionFileTypeImporterEnvironment import (
    VersionFileTypeImporterEnvironment,
)
from Component.Version.VersionImporterEnvironment import VersionImporterEnvironment
from Component.VersionTag.LatestSlotImporterEnvironment import (
    LatestSlotImporterEnvironment,
)
from Component.VersionTag.VersionTagImporterEnvironment import (
    VersionTagImporterEnvironment,
)
from Component.VersionTag.VersionTagOrderImporterEnvironment import (
    VersionTagOrderImporterEnvironment,
)
from Utilities.Trace import Trace, TraceType
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

importer_environment_types:tuple[type[ImporterEnvironment],...] = (
    AccessorTypeImporterEnvironment,
    DataminerImporterEnvironment,
    LatestSlotImporterEnvironment,
    LogImporterEnvironment,
    SerializerImporterEnvironment,
    StructureImporterEnvironment,
    StructureTagImporterEnvironment,
    TablifierImporterEnvironment,
    VersionFileTypeImporterEnvironment,
    VersionImporterEnvironment,
    VersionTagImporterEnvironment,
    VersionTagOrderImporterEnvironment,
)

component_types_dict:dict[str,type[Component]] = {component_type.class_name: component_type for component_type in component_types}

component_group_type_verifier = DictTypeVerifier(dict, str, TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("type", False, str),
    loose=True
))

def print_exceptions(domain:"Domain.Domain", trace:Trace) -> None:
    texts:list[str] = list(trace.stringify())
    failed_component_groups:set[str] = {name() for (object, name, data, trace_type) in trace.objects if trace_type is TraceType.object and isinstance(object, ImporterEnvironment)}
    with open(domain.component_log_file, "wb") as f:
        f.write("\n".join(texts).encode())
    if len(texts) > 0:
        for text in texts:
            print(text)
        raise Exceptions.ComponentParseError(sorted(failed_component_groups), len(texts))

def get_inline_component_function(domain:"Domain.Domain", trace:Trace) -> CreateComponentFunction:
    def create_inline_component(component_data:ComponentTypedDicts, parent_component:Component, assume_type:str|None, path:tuple[str,...]) -> Component|EllipsisType:
        component_name = parent_component.get_inline_component_name(path)
        component_type_str = component_data.get("type", assume_type)
        if component_type_str is None:
            trace.exception(Exceptions.ComponentTypeMissingError(component_name, parent_component.component_group))
            return ...
        component_type = component_types_dict.get(component_type_str)
        if component_type is None:
            trace.exception(Exceptions.UnrecognizedComponentTypeError(component_type_str, f"{domain.name}!{parent_component.component_group}/{component_name}>", list(component_types_dict.keys())))
            return ...
        if component_type.verify_arguments(component_data, trace):
            return ...
        component = component_type(component_data, component_name, domain, parent_component.component_group, None, trace)
        component.inline_parent = parent_component
        return component
    return create_inline_component

def create_components(name:str, data:ComponentGroupFileType, importer_environment:ImporterEnvironment, domain:"Domain.Domain", trace:Trace) -> dict[str,Component]:
    '''Returns a dict of all Components in the Component group.'''
    components:dict[str,Component] = {}
    for index, (component_name, component_data) in enumerate(data.items()):
        with trace.enter(component_name, component_name, component_data): # substitute actual Component for its name, since it's not created yet.
            component_type_str = component_data.get("type", importer_environment.assume_type)
            if component_type_str is None:
                trace.exception(Exceptions.ComponentTypeMissingError(component_name, name))
                continue
            component_type = component_types_dict.get(component_type_str)
            if component_type is None:
                trace.exception(Exceptions.UnrecognizedComponentTypeError(component_type_str, f"{domain.name}!{name}/{component_name}>", list(component_types_dict.keys())))
                continue
            if component_type.verify_arguments(component_data, trace):
                continue
            component = component_type(component_data, component_name, domain, name, index, trace)
            components[component_name] = component
    return components

def get_file(path:Path, importer_environment:ImporterEnvironment) -> ComponentGroupFileType:
    try:
        with open(path, "rt") as f:
            return json.decode_io(f) # type: ignore[reportArgumentType] # stupid types are almost the same but not quite
    except FileNotFoundError:
        if (default_content := importer_environment.get_default_contents()) is not None:
            return default_content
        else:
            raise Exceptions.ImporterEnvironmentFileNotFoundError(path, importer_environment)

def propagate_variables(all_components:dict[str,dict[str,dict[str,Component]]], domain:"Domain.Domain", trace:Trace) -> None:
    all_components_flat:list[Component] = []
    all_components_flat_memo:set[Component] = set()
    for domain_components in all_components.values():
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                for component in components.values():
                    all_components_flat.extend(component.get_all_descendants(all_components_flat_memo, trace))
    print_exceptions(domain, trace)
    components_queue = deque(all_components_flat) # components_queue and unvisited_components should mirror each other
    unvisited_components = all_components_flat_memo # the set of Components that need to be updated or re-updated.
    while len(components_queue) > 0:
        component = components_queue.popleft()
        unvisited_components.remove(component)
        component_has_changed = component.propagate_variables(trace)
        if component_has_changed:
            for parent_component in component.parents:
                if parent_component not in unvisited_components:
                    unvisited_components.add(parent_component)
                    components_queue.append(parent_component)
    print_exceptions(domain, trace)

def create_all_components(domains:Sequence["Domain.Domain"], trace:Trace) -> tuple[dict[str,dict[str,dict[str,Component]]], dict[str,dict[str,ImporterEnvironment]]]:
    all_components:dict[str,dict[str,dict[str,Component]]] = {}
    already_paths:dict[Path,ImporterEnvironment] = {}
    importer_environments:dict[str,dict[str,ImporterEnvironment]] = {}
    for domain in domains:
        importer_environments[domain.name] = {}
        all_components[domain.name] = {}
        for importer_environment_type in importer_environment_types:
            importer_environment = importer_environment_type(domain)
            for file_path in importer_environment.get_component_files():
                name = importer_environment.get_component_group_name(file_path)
                with trace.enter(importer_environment, name, ...):
                    if file_path in already_paths:
                        raise Exceptions.ImporterEnvironmentPathCollisionError(file_path, importer_environment, already_paths[file_path])
                    if name in importer_environments:
                        raise Exceptions.ImporterEnvironmentNameCollisionError(name, importer_environment, importer_environments[domain.name][name])
                    importer_environments[domain.name][name] = importer_environment
                    already_paths[file_path] = importer_environment
                    components_data = get_file(file_path, importer_environment)
                    if importer_environment.single_component:
                        components_data = cast(ComponentGroupFileType, {"": components_data})
                    if component_group_type_verifier.verify(components_data, trace):
                        # avoid creating Component group with wonky component group.
                        continue
                    all_components[domain.name][name] = create_components(name, components_data, importer_environment, domain, trace)
    print_exceptions(domains[-1], trace)
    return all_components, importer_environments

def get_imports(domains:Sequence["Domain.Domain"]) -> dict[str,Sequence[str]]:
    return {domain.name: domain.dependencies_str for domain in domains}

def set_components(all_components:dict[str,dict[str,dict[str,Component]]], domain_imports:dict[str,Sequence[str]], functions:dict[str,ScriptSetSetSet], domain_list:Sequence["Domain.Domain"], trace:Trace) -> None:
    domains:dict[str,Domain] = {domain.name: domain for domain in domain_list}
    for domain_name, domain_components in all_components.items():
        create_inline_component = get_inline_component_function(domains[domain_name], trace)
        script_set_set_set = functions[domain_name]
        imported_set = set(domain_imports[domain_name])
        imported_set.add(domain_name)
        imports = {domain_name: domain_components for domain_name, domain_components in all_components.items() if domain_name in imported_set}
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                for component in components.values():
                    component.set_component(components, imports, script_set_set_set, create_inline_component, trace)
    print_exceptions(domain_list[-1], trace)

def create_finals(all_components:dict[str,dict[str,dict[str,Component]]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain_components in all_components.values():
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                for component in components.values():
                    component_output = component.create_final_component(trace)
                    if component_output is ...:
                        continue
                    component.final = component_output
    print_exceptions(domain, trace)

def link_finals(all_components:dict[str,dict[str,dict[str,Component]]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain_components in all_components.values():
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                for component in components.values():
                    component.link_finals(trace)
    print_exceptions(domain, trace)

def check_components(all_components:dict[str,dict[str,dict[str,Component]]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain_components in all_components.values():
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                for component in components.values():
                    component.check(trace)
    print_exceptions(domain, trace)

def finalize_components(all_components:dict[str,dict[str,dict[str,Component]]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain_components in all_components.values():
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                for component in components.values():
                    component.finalize(trace)
    print_exceptions(domain, trace)

def get_outputs(all_components:dict[str,dict[str,dict[str,Component]]], importer_environments:dict[str,dict[str,ImporterEnvironment]], domain:"Domain.Domain", trace:Trace) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for domain_name, domain_components in all_components.items():
        suboutput:dict[str,Any] = {}
        for name, components in domain_components.items():
            with trace.enter(name, name, components):
                suboutput[name] = importer_environments[domain_name][name].get_output(components, name, trace)
        output[domain_name] = suboutput
    print_exceptions(domain, trace)
    return output

def get_script_referenceable(
    all_components:dict[str,dict[str,dict[str,Component]]],
    primary_domain:"Domain.Domain"
) -> None:
    objects:dict[str,dict[str,dict[str,Any|EllipsisType]]] = {}
    for domain_name, domain_content in all_components.items():
        objects[domain_name] = {}
        for component_group_name, components in domain_content.items():
            objects[domain_name][component_group_name] = {}
            for component_name, component in components.items():
                objects[domain_name][component_group_name][component.name] = component.final if component.script_referenceable else ...
    primary_domain.script_referenceable.update_objects(objects)

def check_for_unused_components(all_components:dict[str,dict[str,dict[str,Component]]], importer_environments:dict[str,dict[str,ImporterEnvironment]], domain:"Domain.Domain", trace:Trace) -> None:
    visited_nodes:set[Component] = set()
    unvisited_nodes:list[Component] = []
    for domain_name, domain_components in all_components.items():
        for name, components in domain_components.items():
            unvisited_nodes.extend(importer_environments[domain_name][name].get_assumed_used_components(components, name, trace))
    print_exceptions(domain, trace)
    while len(unvisited_nodes) > 0:
        unvisited_node = unvisited_nodes.pop()
        if unvisited_node in visited_nodes: continue
        unvisited_nodes.extend(
            neighbor
            for neighbor in unvisited_node.links_to_other_components
            if neighbor not in visited_nodes
        )
        visited_nodes.add(unvisited_node)
    unused_components:Iterable[Component] = (
        component
        for domain_components in all_components.values()
        for components in domain_components.values()
        for component in components.values()
        if component not in visited_nodes
    )
    for unused_component in unused_components:
        print(f"Warning: Unused component: {unused_component}")

def finalize_importer_environments(output:dict[str,dict[str,Any]], importer_environments:dict[str,dict[str,ImporterEnvironment]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain_name, domain_outputs in output.items():
        for name, component_group_output in domain_outputs.items():
            importer_environments[domain_name][name].finalize(component_group_output, output, name, trace)
    print_exceptions(domain, trace)

def check_importer_environments(output:dict[str,dict[str,Any]], importer_environments:dict[str,dict[str,ImporterEnvironment]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain_name, domain_outputs in output.items():
        for name, component_group_output in domain_outputs.items():
            importer_environments[domain_name][name].check(component_group_output, output, name, trace)
    print_exceptions(domain, trace)

def get_all_functions(domain_list:Sequence["Domain.Domain"], domain_imports:dict[str,Sequence[str]]) -> dict[str,ScriptSetSetSet]:
    domains:dict[str,"Domain.Domain"] = {domain.name: domain for domain in domain_list}
    domain_dependencies:Iterable[tuple["Domain.Domain", Iterable["Domain.Domain"]]] = ((domains[domain], (domains[dependency] for dependency in dependencies)) for domain, dependencies in domain_imports.items())
    return {domain.name: ScriptSetSetSet(domain, dependencies) for domain, dependencies in domain_dependencies}

def parse_all_component_groups(domains:Sequence["Domain.Domain"]) -> dict[str,dict[str,Any]]:
    '''
    :domain: A Domain and its dependencies. The primary Domain goes last.
    '''
    trace = Trace()
    all_components, importer_environments = create_all_components(domains, trace)
    domain_imports = get_imports(domains)
    functions = get_all_functions(domains, domain_imports)
    set_components(all_components, domain_imports, functions, domains, trace)
    propagate_variables(all_components, domains[-1], trace)
    create_finals(all_components, domains[-1], trace)
    get_script_referenceable(all_components, domains[-1])
    link_finals(all_components, domains[-1], trace)
    check_components(all_components, domains[-1], trace)
    finalize_components(all_components, domains[-1], trace)
    output = get_outputs(all_components, importer_environments, domains[-1], trace)
    check_for_unused_components(all_components, importer_environments, domains[-1], trace)
    finalize_importer_environments(output, importer_environments, domains[-1], trace)
    check_importer_environments(output, importer_environments, domains[-1], trace)
    return output
