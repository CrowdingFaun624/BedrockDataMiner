import json
import traceback
from collections import deque
from typing import TYPE_CHECKING, Any, cast

from pathlib2 import Path

import Component.Accessor.AccessorComponent as AccessorComponent
import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Accessor.AccessorTypeImporterEnvironment as AccessorTypeImporterEnvironment
import Component.Component as Component
import Component.ComponentFunctions as ComponentFunctions
import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
import Component.DataMiner.DataMinerImporterEnvironment as DataMinerImporterEnvironment
import Component.DataMiner.DataMinerSettingsComponent as DataMinerSettingsComponent
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Structure.BaseComponent as BaseComponent
import Component.Structure.CacheComponent as CacheComponent
import Component.Structure.DictComponent as DictComponent
import Component.Structure.GroupComponent as GroupComponent
import Component.Structure.KeymapComponent as KeymapComponent
import Component.Structure.ListComponent as ListComponent
import Component.Structure.NbtBaseComponent as NbtBaseComponent
import Component.Structure.NbtTagComponent as NbtTagComponent
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureImporterEnvironment as StructureImporterEnvironment
import Component.Structure.TagComponent as TagComponent
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Component.Structure.VolumeComponent as VolumeComponent
import Component.Version.VersionComponent as VersionComponent
import Component.Version.VersionFileComponent as VersionFileComponent
import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent
import Component.Version.VersionFileTypeImporterEnvironment as VersionFileTypeImporterEnvironment
import Component.Version.VersionImporterEnvironment as VersionImporterEnvironment
import Component.VersionTag.LatestSlotComponent as LatestSlotComponent
import Component.VersionTag.LatestSlotImporterEnvironment as LatestSlotImporterEnvironment
import Component.VersionTag.RangeVersionTagAutoAssignerComponent as RangeVersionTagAutoAssignerComponent
import Component.VersionTag.VersionTagComponent as VersionTagComponent
import Component.VersionTag.VersionTagImporterEnvironment as VersionTagImporterEnvironment
import Component.VersionTag.VersionTagOrderComponent as VersionTagOrderComponent
import Component.VersionTag.VersionTagOrderImporterEnvironment as VersionTagOrderImporterEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import DataMiner.DataMinerCollection as DataMinerCollection
    import Downloader.AccessorType as AccessorType
    import Structure.StructureBase as StructureBase
    import Version.Version as Version
    import Version.VersionFileType as VersionFileType
    import Version.VersionTag.VersionTag as VersionTag
    import Version.VersionTag.VersionTagOrder as VersionTagOrder

component_types:list[type[Component.Component]] = [
    AccessorComponent.AccessorComponent,
    AccessorTypeComponent.AccessorTypeComponent,
    BaseComponent.BaseComponent,
    CacheComponent.CacheComponent,
    DataMinerCollectionComponent.DataMinerCollectionComponent,
    DataMinerSettingsComponent.DataMinerSettingsComponent,
    DictComponent.DictComponent,
    GroupComponent.GroupComponent,
    KeymapComponent.KeymapComponent,
    LatestSlotComponent.LatestSlotComponent,
    ListComponent.ListComponent,
    NbtBaseComponent.NbtBaseComponent,
    NbtTagComponent.NbtKeymapTagCompoundComponent,
    NbtTagComponent.NbtTagByteArrayComponent,
    NbtTagComponent.NbtTagCompoundComponent,
    NbtTagComponent.NbtTagIntArrayComponent,
    NbtTagComponent.NbtTagListComponent,
    NbtTagComponent.NbtTagLongArrayComponent,
    NormalizerComponent.NormalizerComponent,
    RangeVersionTagAutoAssignerComponent.RangeVersionTagAutoAssignerComponent,
    TagComponent.TagComponent,
    TypeAliasComponent.TypeAliasComponent,
    VersionComponent.VersionComponent,
    VersionFileComponent.VersionFileComponent,
    VersionFileTypeComponent.VersionFileTypeComponent,
    VersionTagComponent.VersionTagComponent,
    VersionTagOrderComponent.VersionTagOrderComponent,
    VolumeComponent.VolumeComponent,
]

importer_environment_types:list[type[ImporterEnvironment.ImporterEnvironment]] = [
    AccessorTypeImporterEnvironment.AccessorTypeImporterEnvironment,
    DataMinerImporterEnvironment.DataMinerImporterEnvironment,
    LatestSlotImporterEnvironment.LatestSlotImporterEnvironment,
    StructureImporterEnvironment.StructureImporterEnvironment,
    VersionFileTypeImporterEnvironment.VersionFileTypeImporterEnvironment,
    VersionImporterEnvironment.VersionImporterEnvironment,
    VersionTagImporterEnvironment.VersionTagImporterEnvironment,
    VersionTagOrderImporterEnvironment.VersionTagOrderImporterEnvironment,
]

component_types_dict:dict[str,type[Component.Component]] = {component_type.class_name: component_type for component_type in component_types}

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
        raise Exceptions.UnrecognizedComponentTypeError(component_type_str, component_name, "(Must be one of [%s])" % (", ".join(component.class_name for component in component_types),))
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
            raise Exceptions.UnrecognizedComponentTypeError(component_type_str, "%s in %s" % (component_name, name), "(Must be one of [%s])" % (", ".join(component.class_name for component in component_types),))
        component = component_type(component_data, component_name, name, index)
        components[component_name] = component
    return components

def get_file(path:Path) -> ComponentTyping.ComponentGroupFileType:
    with open(path, "rt") as f:
        return json.load(f)

def propagate_variables(all_components:dict[str,dict[str,Component.Component]]) -> None:
    all_components_flat:list[Component.Component] = []
    all_components_flat_memo:set[Component.Component] = set()
    for components in all_components.values():
        for component in components.values(): all_components_flat.extend(component.get_all_descendants(all_components_flat_memo))
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

def parse_all_component_groups() -> dict[str,Any]:
    functions = ComponentFunctions.functions
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

    component_imports:dict[str,dict[str,dict[str,Component.Component]]] = {}
    for name, components in all_components.items():
        component_imports[name] = importer_environments[name].get_imports(components, all_components, name)

    for name, components in all_components.items():
        for component in components.values(): component.set_component(components, component_imports[name], functions, create_inline_component)

    propagate_variables(all_components)

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

    output:dict[str,Any] = {}
    for name, components in all_components.items():
        importer_environment_output, unused_components = importer_environments[name].get_output(components, name)
        for unused_component in unused_components:
            print("Warning: Unused %r in %s." % (unused_component, name))
        output[name] = importer_environment_output

    for name, component_group_output in output.items():
        importer_environment = importer_environments[name]
        importer_environment.finalize(component_group_output, output)

    exceptions:list[Exception] = []
    for name, component_group_output in output.items():
        importer_environment = importer_environments[name]
        exceptions.extend(importer_environment.check(component_group_output, output))

    return output

all_component_groups = parse_all_component_groups()

accessor_types:dict[str,"AccessorType.AccessorType"] = all_component_groups["accessor_types"]
dataminer_collections:dict[str,"DataMinerCollection.DataMinerCollection"] = all_component_groups["dataminer_collections"]
latest_slots:list[str] = all_component_groups["latest_slots"]
structures:dict[str,"StructureBase.StructureBase"] = {component_group_name: component_group for component_group_name, component_group in all_component_groups.items() if component_group_name.startswith("structure/")}
version_file_types:dict[str,"VersionFileType.VersionFileType"] = all_component_groups["version_file_types"]
version_tags_order:"VersionTagOrder.VersionTagOrder" = all_component_groups["version_tags_order"]
version_tags:dict[str,"VersionTag.VersionTag"] = all_component_groups["version_tags"]
versions:dict[str,"Version.Version"] = all_component_groups["versions"]