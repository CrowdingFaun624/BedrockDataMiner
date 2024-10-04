from typing import Any, cast

import Utilities.File as File

__all__ = ["ui_normalize"]

def parse_element_name(raw_element_name:str, namespace:str) -> tuple[str,str|None,str|None]:
    '''Returns the element's name, its superclass's namespace, and the superclass's name.'''
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

def get_namespaces_and_extensions(data:dict[str,File.File[dict[str,dict[str,Any]]]]) -> tuple[dict[str,dict[str,dict[str,Any]]], dict[str,dict[str,tuple[str|None,str|None]]], list[int]]:
    namespaces:dict[str,dict[str,dict[str,Any]]] = {} # {namespace: {element_name: element_data}}
    extensions:dict[str,dict[str,tuple[str|None,str|None]]] = {} # {namespace: {subelement: (superelements_namespace, superelement)}}
    file_hashes:list[int] = []
    for file_name, file in data.items():
        elements = file.data
        file_hashes.append(hash(file))
        namespace = cast(str, elements.pop("namespace"))
        if namespace not in namespaces:
            namespaces[namespace] = {}
            extensions[namespace] = {}
        for raw_element_name, element_data in elements.items():
            element_name, superclass_namespace, superclass_element_name = parse_element_name(raw_element_name, namespace)
            namespaces[namespace][element_name] = element_data
            extensions[namespace][element_name] = (superclass_namespace, superclass_element_name)
    return namespaces, extensions, file_hashes

def get_element_type(element_name:str, namespace:str, element_data:dict[str,Any], namespaces:dict[str,dict[str,dict[str,Any]]], extensions:dict[str,dict[str,tuple[str|None, str|None]]]) -> str|None:
    current_element_name = element_name
    current_element_namespace = namespace
    current_element_data = element_data
    already_elements:set[tuple[str,str]] = set()
    while True:
        if (current_element_namespace, current_element_name) in already_elements:
            raise RuntimeError("Encountered loop trying to find type of element \"%s\" of \"%s\"" % (element_name, namespace))
        already_elements.add((current_element_namespace, current_element_name))
        if "type" in current_element_data:
            return current_element_data["type"]
        elif "anim_type" in current_element_data:
            return current_element_data["anim_type"]
        else:
            next_element_namespace, next_element_name = extensions[current_element_namespace][current_element_name]
            if next_element_namespace is None or next_element_name is None:
                return "unknown"
                # raise RuntimeError("Cannot find type of element \"%s\" of \"%s\"!" % (element_name, namespace))
            try:
                next_element_data = namespaces[next_element_namespace][next_element_name]
            except KeyError:
                return "unknown"
            current_element_name = next_element_name
            current_element_namespace = next_element_namespace
            current_element_data = next_element_data

def get_element_types(namespaces:dict[str,dict[str,dict[str,Any]]], extensions:dict[str,dict[str,tuple[str|None, str|None]]]) -> dict[str,dict[str,str]]:
    element_types:dict[str,dict[str,str]] = {}
    for namespace, elements in namespaces.items():
        element_types[namespace] = {}
        for element_name, element_data in elements.items():
            element_type = get_element_type(element_name, namespace, element_data, namespaces, extensions)
            if element_type is not None:    
                element_types[namespace][element_name] = element_type
    return element_types

def parse_element(element_data:dict[str,list[dict[str,Any]]], element_types:dict[str,dict[str,str]], element_name:str, namespace:str) -> None:
    if "controls" not in element_data: return
    for control in element_data["controls"]:
        if not isinstance(control, dict): continue
        for raw_subelement_name, subelement_data in control.items():
            subelement_name, subelement_superclass_namespace, subelement_superclass_name = parse_element_name(raw_subelement_name, namespace)
            if "$" in raw_subelement_name:
                subelement_type = "unknown"
            elif "type" in subelement_data:
                subelement_type = subelement_data["type"]
            elif "anim_type" in subelement_data:
                subelement_type = subelement_data["anim_type"]
            else:
                assert subelement_superclass_name is not None and subelement_superclass_namespace is not None
                try:
                    subelement_type = element_types[subelement_superclass_namespace][subelement_superclass_name]
                except KeyError:
                    subelement_type = "unknown"
            control[raw_subelement_name] = {subelement_type: subelement_data}
            parse_element(subelement_data, element_types, element_name, namespace)

def parse_elements(namespaces:dict[str,dict[str,dict[str,Any]]], element_types:dict[str,dict[str,str]]) -> None:
    for namespace, elements in namespaces.items():
        for element_name, element_data in elements.items():
            parse_element(element_data, element_types, element_name, namespace)

def ui_normalize(data:dict[str,dict[str,File.File[dict[str,dict[str,Any]]]]]) -> File.FakeFile[dict[str,dict[str,dict[str,Any]]]]:
    files:dict[str,File.File[dict[str,dict[str,Any]]]] = {}
    for resource_pack, resource_pack_files in data.items():
        if len(common_files := (set(files) & set(resource_pack_files))) > 0:
            raise RuntimeError("Duplicate files [%s]" % ", ".join(common_files))
        files.update(resource_pack_files)
    namespaces, extensions, file_hashes = get_namespaces_and_extensions(files)
    element_types = get_element_types(namespaces, extensions)
    parse_elements(namespaces, element_types)
    
    output:dict[str,dict[str,dict[str,Any]]] = {}
    for namespace, elements in namespaces.items():
        output[namespace] = {}
        for element_name, element_data in elements.items():
            superclass_namespace, superclass_element_name = extensions[namespace][element_name]
            if superclass_element_name is None:
                raw_element_name = element_name
            else:
                raw_element_name = "%s@%s.%s" % (element_name, superclass_namespace, superclass_element_name)
            element_type = element_types[namespace][element_name]
            output[namespace][raw_element_name] = {element_type: element_data}
    return File.FakeFile("combined_ui_file", output, hash(tuple(file_hashes)))
