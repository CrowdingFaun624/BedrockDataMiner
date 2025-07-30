from itertools import chain
from types import EllipsisType
from typing import Any, Callable, NoReturn, TypeIs, overload

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Utilities.Scripts import Script
from Utilities.Trace import Trace


class ScriptSet():

    __slots__ = (
        "all_scripts",
        "built_in_objects",
        "domain",
        "domain_scripts",
        "scripts_by_file",
        "scripts_by_name",
    )

    def __init__(
        self,
        domain:"Domain.Domain",
        domain_scripts:dict[tuple[str,str],Script[Any]],
        all_scripts:dict[tuple[str,str],Script],
        scripts_by_name:dict[str,Script],
        scripts_by_file:dict[str,Script],
        built_in_objects:dict[str,Script],
        ) -> None:
        self.domain = domain
        self.domain_scripts = domain_scripts
        self.all_scripts = all_scripts
        self.scripts_by_name = scripts_by_name
        self.scripts_by_file = scripts_by_file
        self.built_in_objects = built_in_objects

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

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

    @overload
    def get[a](self, key:str, source_domain:"Domain.Domain", trace:None=None, full_key:str|None=None, verify_function:Callable[[Any],TypeIs[a]]|None=None, instance:type[a]|None=None, subclass:a|None=None, type_name:str|None=None) -> Script[a]: ...
    @overload
    def get[a](self, key:str, source_domain:"Domain.Domain", trace:Trace, full_key:str|None=None, verify_function:Callable[[Any],TypeIs[a]]|None=None, instance:type[a]|None=None, subclass:a|None=None, type_name:str|None=None) -> Script[a]|EllipsisType: ...
    def get[a](self, key:str, source_domain:"Domain.Domain", trace:Trace|None=None, full_key:str|None=None, verify_function:Callable[[Any],TypeIs[a]]|None=None, instance:type[a]|None=None, subclass:a|None=None, type_name:str|None=None) -> Script[a]|EllipsisType:
        '''
        :key: The name of the object.
        :source: The Component referencing this Script.
        '''
        if full_key is None:
            full_key = key
        output = ...
        if key in self.built_in_objects:
            output = self.built_in_objects[key]
        elif (script := self.scripts_by_name.get(key)) is not None:
            output = script
        elif (script := self.scripts_by_file.get(key)) is not None:
            output = script
        elif len(split_key := key.split(" ", maxsplit=1)) == 2 and (script := self.all_scripts.get((split_key[0], split_key[1]))) is not None:
            output = script
        # cannot find Script, show a nice error message.
        elif len(split_key) == 2 and script is None and not any(file_name == split_key[0] for (file_name, object_name) in self.all_scripts):
            raise_error(Exceptions.UnrecognizedScriptFileNameError(full_key, split_key[0], self.get_options(source_domain)), trace)
        elif len(split_key) == 2 and script is None:
            raise_error(Exceptions.UnrecognizedScriptObjectNameError(full_key, split_key[0], split_key[1], self.get_options(source_domain)), trace)
        elif len(duplications := [script for (file_name, object_name), script in self.all_scripts.items() if file_name == key or object_name == key]) > 0:
            raise_error(Exceptions.ScriptGeneralityError(full_key, duplications, self.get_options(source_domain)), trace)
        elif len(scripts := [script for (file_name, object_name), script in self.domain_scripts.items() if file_name == key or object_name == key]) > 0:
            raise_error(Exceptions.ScriptGeneralityError(full_key, scripts, self.get_options(source_domain)), trace)
        else:
            raise_error(Exceptions.UnrecognizedScriptError(full_key, self.get_options(source_domain)), trace)
        if output is ...:
            return ...
        if verify_function is not None and not verify_function(output.object):
            raise_error(Exceptions.WrongScriptError(full_key, output, type_name, self.get_options(source_domain)), trace)
            return ...
        elif instance is not None and not isinstance(output.object, instance):
            raise_error(Exceptions.WrongScriptError(full_key, output, type_name, self.get_options(source_domain)), trace)
        elif subclass is not None and (not isinstance(output.object, type) or isinstance(subclass, type) and not issubclass(output.object, subclass)):
            raise_error(Exceptions.WrongScriptError(full_key, output, type_name, self.get_options(source_domain)), trace)
        return output

class ScriptSetSet():

    # I assure you this is absolutely necessary

    __slots__ = (
        "domain",
        "script_sets",
    )

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain
        self.script_sets = {domain.name: domain.script_set}
        self.script_sets.update((dependency.name, dependency.script_set) for dependency in domain.dependencies)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

    def get_options(self, domain:"Domain.Domain") -> list[str]:
        return list(chain.from_iterable(script_set.get_options(domain) for script_set in self.script_sets.values()))

    @overload
    def get[a](self, key:str, domain:"Domain.Domain", trace:None=None, verify_function:Callable[[Any],TypeIs[a]]|None=None, instance:type[a]|None=None, subclass:a|None=None, type_name:str|None=None) -> Script[a]: ...
    @overload
    def get[a](self, key:str, domain:"Domain.Domain", trace:Trace, verify_function:Callable[[Any],TypeIs[a]]|None=None, instance:type[a]|None=None, subclass:a|None=None, type_name:str|None=None) -> Script[a]|EllipsisType: ...
    def get[a](self, key:str, domain:"Domain.Domain", trace:Trace|None=None, verify_function:Callable[[Any],TypeIs[a]]|None=None, instance:type[a]|None=None, subclass:a|None=None, type_name:str|None=None) -> Script[a]|EllipsisType:
        if len(split_key := key.split("!", maxsplit=1)) == 2:
            domain_name, subkey = split_key
            if (script_set := self.script_sets.get(domain_name)) is None:
                raise Exceptions.UnrecognizedScriptDomainError(domain_name, key, self.get_options(domain))
            return script_set.get(subkey, domain, trace, key, verify_function, instance, subclass, type_name)
        else:
            return self.script_sets[self.domain.name].get(key, domain, trace)

def raise_error(exception:Exception, trace:Trace|None) -> None|NoReturn:
    if trace is None:
        raise exception
    else:
        trace.exception(exception)

def add_to_deduplicated_dict[K, V](_dict:dict[K, V], key:K, value:V, duplicated_keys:set[K]) -> None:
    if key not in duplicated_keys:
        if key in _dict:
            duplicated_keys.add(key)
            del _dict[key]
        else:
            _dict[key] = value

def import_scripted_objects(domain:"Domain.Domain", built_in_objects:dict[str,Any]) -> ScriptSet:
    '''
    :folder: The subfolder of scripts that contains the desired type.
    :built_in_objects: Basic built-in objects.
    :is_valid_function: A function which verifies if an object is correct.
    '''
    scripts = domain.scripts.scripts
    all_scripts:dict[tuple[str,str],Script] = {}
    scripts_by_file_name:dict[str,Script] = {}
    scripts_by_object_name:dict[str,Script] = {}
    double_file_names:set[str] = set()
    double_object_names:set[str] = set()
    for (file_name, object_name), script in scripts.items():
        all_scripts[file_name, object_name] = script
        add_to_deduplicated_dict(scripts_by_file_name, file_name, script, double_file_names)
        add_to_deduplicated_dict(scripts_by_object_name, object_name, script, double_object_names)
    return ScriptSet(domain, domain.scripts.scripts, all_scripts, scripts_by_object_name, scripts_by_file_name, built_in_objects)
