from typing import TYPE_CHECKING, Any, Callable

import Domain.Domain as Domain
from Component.Group import ScriptFile

if TYPE_CHECKING:
    from Utilities.TypeVerifier import TypedDictTypeVerifier

class Script[a]():

    __slots__ = (
        "object",
        "object_name",
        "type_verifier",
    )

    def __init__(self, object_name:str, object:a, *, type_verifier:"TypedDictTypeVerifier|None"=None) -> None:
        self.object_name:str = object_name
        self.object:a = object

        self.type_verifier = type_verifier

    def __call__(self:"Script[Callable]", *args, **kwargs) -> Any:
        return self.object(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.object_name}>"

class BuiltInScript[a](Script[a]):

    __slots__ = ()

class UserScript[a](Script[a]):
    """
    A Script created by a user in a Domain.
    Use `Component.ComponentFunctions.component_function` to create Scripts.

    :param file_name: The file name of the Script's file, with forward slashes, relative to the Domain's directory, and without the ".py" suffix.
    :param object_name: The name of the Script's object.
    :param object: The primary object of this Script.
    :param domain: The Domain this Script was defined in.
    :param type_verifier: A TypeVerifier used to validate the arguments of the function.
    """

    __slots__ = (
        "domain",
        "file_name",
    )

    def __init__(self, file_name: str, object_name: str, object: a, domain: "Domain.Domain", *, type_verifier: "TypedDictTypeVerifier | None" = None) -> None:
        super().__init__(object_name, object, type_verifier=type_verifier)
        self.file_name = file_name
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name}!{self.file_name} {self.object_name}>"

class Scripts():

    def __init__(self) -> None:
        self.built_in_scripts:dict[str,Script] = {}
        self.built_in_multiple_scripts:dict[str, list[Script]] = {}
        self.domain_name_scripts:dict[tuple["Domain.Domain", str], Script] = {}
        self.domain_name_multiple_scripts:dict[tuple["Domain.Domain", str], list[Script]] = {}
        self.group_scripts:dict["ScriptFile", Script] = {}
        self.group_multiple_scripts:dict["ScriptFile", list[Script]] = {}
        self.group_name_scripts:dict[tuple["ScriptFile", str], Script] = {}
        self.group_name_multiple_scripts:dict[tuple["ScriptFile", str], list[Script]] = {}
        self.name_scripts:dict[str, Script] = {}
        self.name_multiple_scripts:dict[str, list[Script]] = {}

    def add_script(self, script:UserScript) -> None:
        script_file = script.domain.get_script_file(script.file_name)
        add_to_deduplicated_dict((script.domain, script.object_name), script, self.domain_name_scripts, self.domain_name_multiple_scripts)
        add_to_deduplicated_dict(script_file, script, self.group_scripts, self.group_multiple_scripts)
        add_to_deduplicated_dict((script_file, script.object_name), script, self.group_name_scripts, self.group_name_multiple_scripts)
        add_to_deduplicated_dict(script.object_name, script, self.name_scripts, self.name_multiple_scripts)

    def add_built_in_script(self, script:BuiltInScript) -> None:
        add_to_deduplicated_dict(script.object_name, script, self.name_scripts, self.name_multiple_scripts)
        add_to_deduplicated_dict(script.object_name, script, self.built_in_scripts, self.built_in_multiple_scripts)

    def add_builtin(self, script:BuiltInScript) -> None:
        add_to_deduplicated_dict(script.object_name, script, self.name_scripts, self.name_multiple_scripts)
        # TODO: better solution please

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

scripts = Scripts()

def add_to_deduplicated_dict[K, V](key:K, value:V, _dict:dict[K, V], duplicates_dict:dict[K, list[V]]) -> None:
    if (duplicates := duplicates_dict.get(key, None)) is not None:
        duplicates.append(value)
        return
    elif (already := _dict.get(key, None)) is not None:
        del _dict[key]
        duplicates_dict[key] = [already, value]
    else:
        _dict[key] = value
