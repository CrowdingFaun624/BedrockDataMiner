from itertools import chain
from typing import Any, Callable, Iterable, TypeIs

import Component.Component as Component
import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts


class ScriptSet[a]():

    __slots__ = (
        "all_scripts",
        "built_in_objects",
        "domain",
        "domain_scripts",
        "folder",
        "scripts_by_file",
        "scripts_by_name",
        "type_name",
    )

    def __init__(
        self,
        domain:"Domain.Domain",
        domain_scripts:dict[tuple[str,str],Scripts.Script[Any]],
        all_scripts:dict[tuple[str,str],Scripts.Script[a]],
        scripts_by_name:dict[str,Scripts.Script],
        scripts_by_file:dict[str,Scripts.Script],
        built_in_objects:dict[str,a],
        folder:str,
        type_name:str,
        ) -> None:
        self.domain = domain
        self.domain_scripts = domain_scripts
        self.all_scripts = all_scripts
        self.scripts_by_name = scripts_by_name
        self.scripts_by_file = scripts_by_file
        self.built_in_objects = built_in_objects
        self.folder = folder
        self.type_name = type_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.type_name}\" of {self.domain.name}>"

    def get_options(self, source_domain:"Domain.Domain") -> list[str]:
        options:list[str] = []
        options.extend(self.built_in_objects.keys())
        options.extend(f"{self.domain.name}!{file_name} {object_name}" for file_name, object_name in self.all_scripts)
        options.extend(f"{self.domain.name}!{file_name}" for file_name in self.scripts_by_file)
        options.extend(f"{self.domain.name}!{object_name}" for object_name in self.scripts_by_name)
        if self.domain is source_domain:
            options.extend(f"{file_name} {object_name}" for file_name, object_name in self.all_scripts)
            options.extend(f"{file_name}" for file_name in self.scripts_by_file)
            options.extend(f"{object_name}" for object_name in self.scripts_by_name)
        return options

    def get(self, key:str, source_domain:"Domain.Domain", full_key:str|None=None, ) -> a:
        '''
        :key: The name of the object.
        :source: The Component referencing this Script.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this Script.
        '''
        if full_key is None:
            full_key = key
        if key in self.built_in_objects:
            return self.built_in_objects[key]
        elif (script := self.scripts_by_name.get(key)) is not None:
            return script.object
        elif (script := self.scripts_by_file.get(key)) is not None:
            return script.object
        elif len(split_key := key.split(" ", maxsplit=1)) == 2 and (script := self.all_scripts.get((split_key[0], split_key[1]))) is not None:
            return script.object
        # cannot find Script, show a nice error message.
        elif len(split_key) == 2 and (script := self.domain_scripts.get((split_key[0], split_key[1]))) is not None:
            raise Exceptions.WrongScriptError(full_key, script, self.type_name, self.get_options(source_domain))
        elif len(split_key) == 2 and script is None and not any(file_name == split_key[0] for (file_name, object_name) in self.all_scripts):
            raise Exceptions.UnrecognizedScriptFileNameError(full_key, split_key[0], self.get_options(source_domain))
        elif len(split_key) == 2 and script is None:
            raise Exceptions.UnrecognizedScriptObjectNameError(full_key, split_key[0], split_key[1], self.get_options(source_domain))
        elif len(split_key) == 2 and script is None and len(file_names := [file_name for (file_name, object_name), script in self.domain_scripts.items() if file_name == split_key[0]]) > 0:
            raise Exceptions.WrongScriptFileError(full_key, file_names[0], self.type_name, self.get_options(source_domain))
        elif len(duplications := [script for (file_name, object_name), script in self.all_scripts.items() if file_name == key or object_name == key]) > 0:
            raise Exceptions.ScriptGeneralityError(full_key, duplications, self.get_options(source_domain))
        elif len(scripts := [script for (file_name, object_name), script in self.domain_scripts.items() if file_name == key or object_name == key]) > 0:
            raise Exceptions.ScriptGeneralityError(full_key, scripts, self.get_options(source_domain))
        else:
            raise Exceptions.UnrecognizedScriptError(full_key, self.get_options(source_domain))

class ScriptSetSet[a]():

    # I assure you this is absolutely necessary

    __slots__ = (
        "domain",
        "script_sets",
    )

    def __init__(self, domain:"Domain.Domain", script_sets:dict[str,ScriptSet[a]]) -> None:
        self.domain = domain
        self.script_sets = script_sets

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name} in \"{next(iter(self.script_sets.values())).folder}\">"

    def get_options(self, source:"Component.Component") -> list[str]:
        return list(chain.from_iterable(script_set.get_options(source.domain) for script_set in self.script_sets.values()))

    def get(self, key:str, source:"Component.Component") -> a:
        if len(split_key := key.split("!", maxsplit=1)) == 2:
            domain_name, subkey = split_key
            if (script_set := self.script_sets.get(domain_name)) is None:
                raise Exceptions.UnrecognizedScriptDomainError(domain_name, key, self.get_options(source))
            return script_set.get(subkey, source.domain, key)
        else:
            return self.script_sets[self.domain.name].get(key, source.domain)

class ScriptSetSetSet():

    # yup I need this one too.

    __slots__ = (
        "accessor_classes",
        "callables",
        "dataminer_classes",
        "delegate_classes",
        "domain",
        "serializer_classes",
        "version_provider_classes",
    )

    def __init__(self, domain:"Domain.Domain", dependencies:Iterable["Domain.Domain"]) -> None:
        all_domains = list(dependencies)
        all_domains.append(domain)
        self.domain = domain
        self.callables = ScriptSetSet(domain, {domain.name: domain.callables for domain in all_domains})
        self.accessor_classes = ScriptSetSet(domain, {domain.name: domain.accessor_classes for domain in all_domains})
        self.dataminer_classes = ScriptSetSet(domain, {domain.name: domain.dataminer_classes for domain in all_domains})
        self.delegate_classes = ScriptSetSet(domain, {domain.name: domain.delegate_classes for domain in all_domains})
        self.serializer_classes = ScriptSetSet(domain, {domain.name: domain.serializer_classes for domain in all_domains})
        self.version_provider_classes = ScriptSetSet(domain, {domain.name: domain.version_provider_classes for domain in all_domains})

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

def add_to_deduplicated_dict[K, V](_dict:dict[K, V], key:K, value:V, duplicated_keys:set[K]) -> None:
    if key not in duplicated_keys:
        if key in _dict:
            duplicated_keys.add(key)
            del _dict[key]
        else:
            _dict[key] = value

def import_scripted_objects[a](folder:str, domain:"Domain.Domain", built_in_objects:dict[str,a], is_valid_function:Callable[[Any],TypeIs[a]], type_name:str) -> ScriptSet[a]:
    '''
    :folder: The subfolder of scripts that contains the desired type.
    :built_in_objects: Basic built-in objects.
    :required_type: Type that Python scripts must export.
    '''
    scripts = domain.scripts.scripts
    all_scripts:dict[tuple[str,str],Scripts.Script[a]] = {}
    scripts_by_file_name:dict[str,Scripts.Script[a]] = {}
    scripts_by_object_name:dict[str,Scripts.Script[a]] = {}
    double_file_names:set[str] = set()
    double_object_names:set[str] = set()
    for (file_name, object_name), script in scripts.items():
        if not is_valid_function(script.object):
            continue
        all_scripts[file_name, object_name] = script
        add_to_deduplicated_dict(scripts_by_file_name, file_name, script, double_file_names)
        add_to_deduplicated_dict(scripts_by_object_name, object_name, script, double_object_names)
    return ScriptSet(domain, domain.scripts.scripts, all_scripts, scripts_by_object_name, scripts_by_file_name, built_in_objects, folder, type_name)

def import_scripted_types[a](folder:str, domain:"Domain.Domain", built_in_classes:dict[str,type[a]], required_superclass:type[a]) -> ScriptSet[type[a]]:
    '''
    :folder: The subfolder of scripts that contains the desired type.
    :built_in_classes: Basic built-in classes.
    :required_superclass: Type that Python scripts must export.
    '''
    scripts = domain.scripts.scripts
    all_scripts:dict[tuple[str,str],Scripts.Script[type[a]]] = {}
    scripts_by_file_name:dict[str,Scripts.Script[type[a]]] = {}
    scripts_by_object_name:dict[str,Scripts.Script[type[a]]] = {}
    double_file_names:set[str] = set()
    double_object_names:set[str] = set()
    for (file_name, object_name), script in scripts.items():
        if not isinstance(script.object, type):
            continue
        if not issubclass(script.object, required_superclass):
            continue
        all_scripts[file_name, object_name] = script
        add_to_deduplicated_dict(scripts_by_file_name, file_name, script, double_file_names)
        add_to_deduplicated_dict(scripts_by_object_name, object_name, script, double_object_names)
    return ScriptSet(domain, domain.scripts.scripts, all_scripts, scripts_by_object_name, scripts_by_file_name, built_in_classes, folder, required_superclass.__name__)
