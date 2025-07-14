from pathlib import Path
from typing import cast

from pyjson5 import Json5Exception, decode_io

import Domain.Domain as Domain
from Component.Component import Component
from Component.ComponentTypes import component_types
from Component.ComponentTyping import GroupFileType
from Component.InheritedComponent import InheritedComponent
from Utilities.Exceptions import (
    ComponentFileError,
    ComponentTypeMissingError,
    GroupAliasDomainError,
    UnrecognizedComponentTypeError,
    UnrecognizedGroupAliasError,
)
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

component_types_dict:dict[str,type[Component]] = {component_type.class_name: component_type for component_type in component_types}

class Group():
    '''
    Basically a file of Components.
    '''

    component_type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("type", False, str),
        TypedDictKeyTypeVerifier("inherit", False, str),
        loose=True,
    )
    group_type_verifier = DictTypeVerifier(dict, str, component_type_verifier)
    default_type_type_verifier = EnumTypeVerifier({component_type.class_name for component_type in component_types} | {None})
    group_aliases_type_verifier = DictTypeVerifier(dict, str, str)

    __slots__ = (
        "components",
        "default_type",
        "domain",
        "group_aliases",
        "is_single_component",
        "name",
        "path",
    )

    def __init__(self, domain:"Domain.Domain", file_path:Path, trace:Trace) -> None:
        self.domain:"Domain.Domain" = domain
        self.path:Path = file_path
        self.name:str = file_path.relative_to(domain.assets_directory).as_posix().removesuffix(file_path.suffix)

        self.is_single_component:bool
        self.default_type:str|None
        self.group_aliases:dict[str,str]
        self.components:dict[str,Component] = self._get_components(trace)

    def create_components(self, contents:GroupFileType, trace:Trace) -> dict[str,Component]:
        '''Returns a dict of all Components in the Group.'''
        components:dict[str,Component] = {}
        for index, (component_name, component_data) in enumerate(contents.items()):
            with trace.enter(component_name, component_name, component_data): # substitute actual Component for its name, since it's not created yet.
                if "inherit" in component_data:
                    components[component_name] = InheritedComponent(component_data, component_name, self.domain, self, index, trace)
                    # InheritedComponents do not have their arguments verified nor their Fields initialized.
                    continue
                component_type_str = component_data.get("type", self.default_type)
                if component_type_str is None:
                    trace.exception(ComponentTypeMissingError(component_name, self))
                    continue
                component_type = component_types_dict.get(component_type_str)
                if component_type is None:
                    if "#" in component_type_str:
                        message = "(Expressions are not allowed in the \"type\" field.)"
                    else: message = None
                    trace.exception(UnrecognizedComponentTypeError(component_type_str, f"{self.domain.name}!{self.name}/{component_name}>", list(component_types_dict.keys()), message))
                    continue
                component = component_type(component_data, component_name, self.domain, self, index, trace)
                if component.abstract or not component.init(trace):
                    components[component_name] = component
        return components

    def _get_components(self, trace:Trace) -> dict[str,Component]:
        try:
            with open(self.path, "rt") as f:
                contents:GroupFileType = decode_io(f)
        except Json5Exception as e:
            with open(self.path, "rb") as f:
                byte_contents = f.read()
            raise ComponentFileError(self.path, byte_contents)
        self.default_type = cast(str, contents.pop("default_type", None)) if isinstance(contents, dict) else None
        self.group_aliases = cast(dict[str,str], contents.pop("group_aliases", {}))
        # use any instead of or to make sure it reports errors for both.
        if any([self.default_type_type_verifier.verify(self.default_type, trace), self.group_aliases_type_verifier.verify(self.group_aliases, trace)]):
            return {}
        self.is_single_component = "type" in contents or "inherit" in contents
        if self.is_single_component:
            contents = {"": contents} # type: ignore
        if self.is_single_component and self.component_type_verifier.verify(contents, trace):
            return {}
        elif not self.is_single_component and self.group_type_verifier.verify(contents, trace):
            return {}

        return self.create_components(contents, trace)

    def verify_group_aliases(self, all_groups:dict[str,"Group"], trace:Trace) -> None:
        with trace.enter_key("group_aliases", self.group_aliases):
            for alias, target in self.group_aliases.items():
                with trace.enter_key(alias, target):
                    if "!" in alias:
                        trace.exception(GroupAliasDomainError(alias, target))
                        continue
                    if target not in all_groups:
                        if alias == target:
                            message = "(The alias and target are the same)"
                        elif alias in all_groups:
                            message = f"(while \"{alias}\" is a recognized group, so you have your key and value backwards)"
                        elif "#" in target or "$" in target or "#" in alias or "$" in alias:
                            message = "(Group aliases do not support Variables or Expressions)"
                        else: message = None
                        trace.exception(UnrecognizedGroupAliasError(target, alias, list(all_groups.keys()), message))
                        continue

    @property
    def full_name(self) -> str:
        return f"{self.domain.name}!{self.name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name}!{self.name}>"

    def __hash__(self) -> int:
        return hash((self.domain, self.name))
