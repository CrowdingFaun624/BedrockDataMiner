from collections import deque
from itertools import chain
from pathlib import Path
from types import EllipsisType
from typing import Any, Iterable, Sequence

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.Group import Group, component_types_dict
from Component.InheritedComponent import InheritedComponent
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace, TraceType


def print_exceptions(domain:"Domain.Domain", trace:Trace) -> None:
    texts:list[str] = list(trace.stringify())
    failed_groups:set[str] = {name() for (object, name, data, trace_type) in trace.objects if trace_type is TraceType.object and isinstance(object, Group)}
    if len(texts) > 0:
        with open(domain.component_log_file, "wb") as f:
            f.write("\n".join(texts).encode())
        for text in texts:
            print(text)
        raise Exceptions.ComponentParseError(sorted(failed_groups), len(texts))

def get_inline_component_function(domain:"Domain.Domain", trace:Trace) -> CreateComponentFunction:
    # This function does not resolve inherited Components; it is resolved in Field.refer_to_component
    def create_inline_component(component_data:ComponentTypedDicts, parent_component:Component, default_type:str|None, path:tuple[str,...]) -> Component|EllipsisType:
        component_name = parent_component.get_inline_component_name(path)
        if "inherit" in component_data:
            component = InheritedComponent(component_data, component_name, domain, parent_component.group, None, trace)
            component.inline_parent = parent_component
            return component
        component_type_str = component_data.get("type", default_type)
        if component_type_str is None:
            trace.exception(Exceptions.ComponentTypeMissingError(component_name, parent_component.group))
            return ...
        component_type = component_types_dict.get(component_type_str)
        if component_type is None:
            if "#" in component_type_str:
                message = "(Expressions are not allowed in the \"type\" field.)"
            else: message = None
            trace.exception(Exceptions.UnrecognizedComponentTypeError(component_type_str, f"{domain.name}!{parent_component.group.name}/{component_name}>", list(component_types_dict.keys()), message))
            return ...
        component = component_type(component_data, component_name, domain, parent_component.group, None, trace)
        component.inline_parent = parent_component
        if not component.abstract and component.init(trace): # verifies types and initializes Fields.
            return ...
        return component
    return create_inline_component

def get_all_component_files(domain:"Domain.Domain") -> Sequence[Path]:
    output:list[Path] = []
    for path in domain.assets_directory.iterdir():
        if path.name in ("data", "lib", "log", "domain.json"): continue
        if path.is_dir():
            output.extend(path.rglob("*.json"))
        elif path.is_file() and path.suffix == ".json":
            output.append(path)
    return output

def propagate_variables(all_components:dict["Domain.Domain",list[Group]], domain:"Domain.Domain", trace:Trace) -> None:
    all_components_flat:list[Component] = []
    all_components_flat_memo:set[Component] = set()
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                with trace.enter(group, group.name, ...):
                    all_components_flat.extend(chain.from_iterable(component.get_all_descendants(all_components_flat_memo, trace) for component in group.components.values()))
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

def create_groups(domains:Sequence["Domain.Domain"], trace:Trace) -> dict["Domain.Domain",list[Group]]:
    output:dict["Domain.Domain",list[Group]] = {}
    for domain in domains:
        with trace.enter(domain, domain.name, ...):
            output[domain] = []
            for file_path in get_all_component_files(domain):
                with trace.enter(file_path, file_path.relative_to(domain.assets_directory).as_posix().removesuffix(file_path.suffix), ...):
                    output[domain].append(Group(domain, file_path, trace))
    print_exceptions(domains[-1], trace)
    for domain, groups in output.items():
        with trace.enter(domain, domain.name, ...):
            group_names = {group.name: group for group in groups}
            for group in groups:
                with trace.enter(group, group.name, ...):
                    group.verify_group_aliases(group_names, trace)
    print_exceptions(domains[-1], trace)
    return output

def get_imports(domains:Sequence["Domain.Domain"]) -> dict["Domain.Domain",Sequence["Domain.Domain"]]:
    return {domain: domain.dependencies for domain in domains}

def inheritance(all_components:dict["Domain.Domain",list[Group]], primary_domain:"Domain.Domain", functions:dict["Domain.Domain", "ScriptSetSetSet"], trace:Trace) -> None:
    global_groups:dict[str,dict[str,Group]] = {domain.name: {group.name: group for group in groups} for domain, groups in all_components.items()}
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            create_inline_component = get_inline_component_function(domain, trace)
            for group in groups:
                with trace.enter(group, group.name, ...):
                    for component_name, component in group.components.items():
                        new_component = component.inheritance(set(), global_groups, {}, functions[domain], create_inline_component, trace)
                        if new_component is ...: # an error occurred.
                            continue
                        group.components[component_name] = new_component
    print_exceptions(primary_domain, trace)

def set_components(all_components:dict["Domain.Domain",list[Group]], domain_imports:dict["Domain.Domain",Sequence["Domain.Domain"]], primary_domain:"Domain.Domain", functions:dict["Domain.Domain",ScriptSetSetSet], trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            create_inline_component = get_inline_component_function(domain, trace)
            script_set_set_set = functions[domain]
            imported_set = set(domain_imports[domain])
            imported_set.add(domain)
            imports = {domain.name: {group.name: group for group in groups} for domain, groups in all_components.items() if domain in imported_set}
            for group in groups:
                with trace.enter(group, group.name, ...):
                    for component in group.components.values():
                        component.set_component(group, imports, script_set_set_set, create_inline_component, trace)
    print_exceptions(primary_domain, trace)

def create_finals(all_components:dict["Domain.Domain",list[Group]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                with trace.enter(group, group.name, ...):
                    for component in group.components.values():
                        component_output = component.create_final(trace)
                        if component_output is ...: # happens if create_final_component has an error or component is abstract
                            continue
                        component.final = component_output
    print_exceptions(domain, trace)

def link_finals(all_components:dict["Domain.Domain",list[Group]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                with trace.enter(group, group.name, ...):
                    for component in group.components.values():
                        component.link_final(trace)
    print_exceptions(domain, trace)

def check_components(all_components:dict["Domain.Domain",list[Group]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                with trace.enter(group, group.name, ...):
                    for component in group.components.values():
                        component.check(trace)
    print_exceptions(domain, trace)

def finalize_components(all_components:dict["Domain.Domain",list[Group]], domain:"Domain.Domain", trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            for group in groups:
                remove_components:list[str] = []
                with trace.enter(group, group.name, ...):
                    for component in group.components.values():
                        component.finalize(trace)
                        if component.abstract:
                            remove_components.append(component.name)
                    for remove_component in remove_components:
                        del group.components[remove_component]
    print_exceptions(domain, trace)

def get_script_referenceable(
    all_components:dict["Domain.Domain",list[Group]],
    primary_domain:"Domain.Domain"
) -> None:
    objects:dict[str,dict[str,dict[str,Any|EllipsisType]]] = {}
    for domain, groups in all_components.items():
        objects[domain.name] = {}
        for group in groups:
            objects[domain.name][group.name] = {}
            for component in group.components.values():
                if not component.abstract:
                    objects[domain.name][group.name][component.name] = component.final if component.script_referenceable else ...
    primary_domain.script_referenceable.update_objects(objects)

def check_for_unused_components(all_components:dict["Domain.Domain",list[Group]], domain:"Domain.Domain", trace:Trace) -> None:
    visited_nodes:set[Component] = set()
    unvisited_nodes:list[Component] = []
    for domain, groups in all_components.items():
        for group in groups:
            unvisited_nodes.extend(component for component in group.components.values() if component.assume_used)
    while len(unvisited_nodes) > 0:
        unvisited_node = unvisited_nodes.pop()
        if unvisited_node in visited_nodes: continue
        unvisited_nodes.extend(
            neighbor
            for neighbor in unvisited_node.links_to_other_components
            if neighbor not in visited_nodes
        )
        visited_nodes.add(unvisited_node)
        if unvisited_node.inherit_parent is not None:
            visited_nodes.add(unvisited_node.inherit_parent)
    unused_components:Iterable[Component] = (
        component
        for groups in all_components.values()
        for group in groups
        for component in group.components.values()
        if component not in visited_nodes
    )
    for unused_component in unused_components:
        print(f"Warning: Unused component: {unused_component}")

def get_all_functions(domain_imports:dict["Domain.Domain",Sequence["Domain.Domain"]]) -> dict["Domain.Domain",ScriptSetSetSet]:
    return {domain: ScriptSetSetSet(domain, dependencies) for domain, dependencies in domain_imports.items()}

def parse_all_groups(domains:Sequence["Domain.Domain"]) -> dict["Domain.Domain",list[Group]]:
    '''
    :domain: A Domain and its dependencies. The primary Domain goes last.
    '''
    trace = Trace()
    groups = create_groups(domains, trace)
    domain_imports = get_imports(domains)
    functions = get_all_functions(domain_imports)
    inheritance(groups, domains[-1], functions, trace)
    set_components(groups, domain_imports, domains[-1], functions, trace)
    propagate_variables(groups, domains[-1], trace)
    create_finals(groups, domains[-1], trace)
    get_script_referenceable(groups, domains[-1])
    link_finals(groups, domains[-1], trace)
    check_components(groups, domains[-1], trace)
    finalize_components(groups, domains[-1], trace)
    check_for_unused_components(groups, domains[-1], trace)
    return groups
