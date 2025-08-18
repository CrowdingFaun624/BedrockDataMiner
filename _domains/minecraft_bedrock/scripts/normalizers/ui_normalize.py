from typing import Any, Mapping, Sequence, cast

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer, SerializerCreator
from Utilities.File import FakeFile, File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

CONTROLS_KEYS = ("controls", "+controls")
"""
Keys of items that contain nested elements.
"""

def parse_element_name(raw_element_name:str, namespace:str) -> tuple[str,str|None,str|None]:
    """
    Returns the element's name, its superclass's namespace, and the superclass's name.
    """
    if "@" in raw_element_name:
        element_name, superclass = raw_element_name.split("@", 1)
        if "." in superclass:
            superclass_namespace, superclass_element_name = superclass.split(".", 1)
        else:
            superclass_namespace = namespace
            superclass_element_name = superclass
    else:
        element_name = raw_element_name
        superclass_namespace, superclass_element_name = None, None
    return element_name, superclass_namespace, superclass_element_name

def get_namespaces_and_extensions(data:dict[str,File[Mapping[str,Mapping[str,Any]]]], serializer:Serializer) -> tuple[dict[str,dict[str,Mapping[str,Any]]], dict[str,dict[str,tuple[str|None,str|None]]], list[int]]:
    namespaces:dict[str,dict[str,Mapping[str,Any]]] = {} # {namespace: {element_name: element_data}}
    extensions:dict[str,dict[str,tuple[str|None,str|None]]] = {} # {namespace: {subelement: (superelements_namespace, superelement)}}
    file_hashes:list[int] = []
    for file_name, file in data.items():
        elements = file.read(serializer)
        file_hashes.append(hash(file))
        namespace = cast(str, elements["namespace"])
        if namespace not in namespaces:
            namespaces[namespace] = {}
            extensions[namespace] = {}
        for raw_element_name, element_data in elements.items():
            if raw_element_name == "namespace": continue
            element_name, superclass_namespace, superclass_element_name = parse_element_name(raw_element_name, namespace)
            namespaces[namespace][element_name] = element_data
            extensions[namespace][element_name] = (superclass_namespace, superclass_element_name)
    return namespaces, extensions, file_hashes

def get_element_type(element_name:str, namespace:str, element_data:Mapping[str,Any], namespaces:dict[str,dict[str,Mapping[str,Any]]], extensions:dict[str,dict[str,tuple[str|None, str|None]]]) -> str:
    current_element_name = element_name
    current_element_namespace = namespace
    current_element_data = element_data
    already_elements:set[tuple[str,str]] = set()
    while True:
        if (current_element_namespace, current_element_name) in already_elements:
            # raise RuntimeError(f"Encountered loop trying to find type of element \"{element_name}\" of \"{namespace}\"")
            return "unknown"
        already_elements.add((current_element_namespace, current_element_name))
        if "type" in current_element_data:
            return current_element_data["type"]
        elif "anim_type" in current_element_data:
            return current_element_data["anim_type"]
        else:
            next_element_namespace, next_element_name = extensions[current_element_namespace][current_element_name]
            if next_element_namespace is None or next_element_name is None:
                return "unknown"
                # raise RuntimeError(f"Cannot find type of element \"{element_name}\" of \"{namespace}\"!")
            try:
                next_element_data = namespaces[next_element_namespace][next_element_name]
            except KeyError:
                return "unknown"
            current_element_name = next_element_name
            current_element_namespace = next_element_namespace
            current_element_data = next_element_data

def get_element_types(namespaces:dict[str,dict[str,Mapping[str,Any]]], extensions:dict[str,dict[str,tuple[str|None, str|None]]]) -> dict[str,dict[str,str]]:
    element_types:dict[str,dict[str,str]] = {}
    for namespace, elements in namespaces.items():
        element_types[namespace] = {}
        for element_name, element_data in elements.items():
            element_type = get_element_type(element_name, namespace, element_data, namespaces, extensions)
            if element_type is not None:
                element_types[namespace][element_name] = element_type
    return element_types

def parse_element(element_data:Mapping[str,Any], element_types:dict[str,dict[str,str]], element_name:str, namespace:str) -> dict[str,Any]:
    output:dict[str,Any] = {}
    for key, value in element_data.items():
        if key not in CONTROLS_KEYS:
            output[key] = value
            continue
        value: Sequence[Mapping[str,Mapping[str,Any]]]
        output_controls:list[Mapping[str,Mapping[str,Any]]] = []
        for control in value:
            output_control:dict[str,Mapping[str,Any]] = {}
            if not isinstance(control, dict): continue
            for raw_subelement_name, subelement_data in control.items():
                subelement_name, subelement_superclass_namespace, subelement_superclass_name = parse_element_name(raw_subelement_name, namespace)
                if "$" in raw_subelement_name:
                    new_element = subelement_data
                elif "type" in subelement_data:
                    new_element = subelement_data
                elif "anim_type" in subelement_data:
                    new_element = {key: value for key, value in subelement_data.items()}
                    new_element["type"] = new_element.pop("anim_type")
                else:
                    assert subelement_superclass_name is not None and subelement_superclass_namespace is not None
                    try:
                        subelement_type = element_types[subelement_superclass_namespace][subelement_superclass_name]
                    except KeyError:
                        subelement_type = None
                        new_element = subelement_data
                    else:
                        if subelement_type is not None:
                            new_element = {key: value for key, value in subelement_data.items()}
                            new_element["type"] = subelement_type
                output_control[raw_subelement_name] = parse_element(new_element, element_types, element_name, namespace)
            output_controls.append(output_control)
        output[key] = output_controls
    return output

def parse_elements(namespaces:dict[str,dict[str,Mapping[str,Any]]], element_types:dict[str,dict[str,str]]) -> dict[str,dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,dict[str,Any]]] = {}
    for namespace, elements in namespaces.items():
        output[namespace] = {}
        for element_name, element_data in elements.items():
            output[namespace][element_name] = parse_element(element_data, element_types, element_name, namespace)
    return output

@component_function(no_arguments=True)
def choose_ui_type(data:Mapping[str,str]) -> str:
    if (output := data.get("type")) is not None: return output
    elif (output := data.get("anim_type")) is not None: return output
    return "unknown"

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, SerializerCreator),
))
def ui_normalize(data:Mapping[str,Mapping[str,File[Mapping[str,Mapping[str,Any]]]]], serializer:SerializerCreator) -> FakeFile[dict[str,dict[str,dict[str,Any]]]]:
    files:dict[str,File[Mapping[str,Mapping[str,Any]]]] = {}
    for resource_pack, resource_pack_files in data.items():
        if len(common_files := (set(files) & set(resource_pack_files))) > 0:
            continue
            # raise RuntimeError(f"Duplicate files [{", ".join(common_files)}]")
        files.update(resource_pack_files)
    namespaces, extensions, file_hashes = get_namespaces_and_extensions(files, serializer.serializer)
    element_types = get_element_types(namespaces, extensions)
    parsed_elements = parse_elements(namespaces, element_types)

    output:dict[str,dict[str,dict[str,Any]]] = {}
    for namespace, elements in parsed_elements.items():
        output[namespace] = {}
        for element_name, element_data in elements.items():
            superclass_namespace, superclass_element_name = extensions[namespace][element_name]
            if superclass_element_name is None:
                raw_element_name = element_name
            else:
                raw_element_name = f"{element_name}@{superclass_namespace}.{superclass_element_name}"
            element_type = element_types[namespace][element_name]
            element_data["type"] = element_type
            output[namespace][raw_element_name] = element_data
    return FakeFile("combined_ui_file", output, None, hash(tuple(file_hashes)))
