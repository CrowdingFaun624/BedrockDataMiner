from itertools import chain
from pathlib import Path
from types import EllipsisType
from typing import TYPE_CHECKING, Iterable, Mapping

import Domain.Domain as Domain
from Component.Field.Errors import Errors
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.DomainField import DomainField
    from Component.Field.FieldFactory import FieldFactory
    from Component.Field.GroupField import GroupField
    from Component.Reader import Reader

class Aliases():

    __slots__ = (
        "domain_aliases",
        "error",
        "group_aliases",
    )

    def __init__(self, domain_aliases:Mapping[str,"FieldFactory[DomainField]"], group_aliases:Mapping[str,"FieldFactory[GroupField]"], error:Errors) -> None:
        self.domain_aliases: Mapping[str,"FieldFactory[DomainField]"] = domain_aliases
        self.group_aliases: Mapping[str,"FieldFactory[GroupField]"] = group_aliases
        self.error = error

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.domain_aliases)} {len(self.group_aliases)}>"

class GroupSettings():

    __slots__ = (
        "aliases",
        "error",
    )

    def __init__(self, aliases:Aliases, error:Errors) -> None:
        self.aliases = aliases
        self.error = error.narrow(self.aliases.error)

    def set_field(self, domain:"Domain.Domain", group:"Group", trace:Trace) -> None:
        for index, (field_name, field) in enumerate(self.aliases.domain_aliases.items()):
            if not field.abstract:
                field.set_field(group, field_name, f"{domain.name}!{group.name}<settings><aliases>{field_name}", index, trace, is_inline=False)
        for index, (field_name, field) in enumerate(self.aliases.group_aliases.items()):
            if not field.abstract:
                field.set_field(group, field_name, f"{domain.name}!{group.name}<settings><aliases>{field_name}", index, trace, is_inline=False)

class GroupObject():
    """
    Object representing a directory or file.
    """

    __slots__ = (
        "parent",
        "path",
        "path_name",
    )

    name:str
    """
    Name for error messages. Should be like ".cmp file" or "directory".
    """

    def __init__(self, path:Path, path_name:str, parent:"GroupObject|None") -> None:
        self.path = path
        self.path_name = path_name
        self.parent = parent

    def get_parent(self, trace:Trace) -> tuple["GroupObject|EllipsisType", Errors]:
        if self.parent is None:
            trace.exception(RuntimeError(f"{self} does not have a parent"))
            return ..., Errors.create_field
        return self.parent, Errors.fine

    def get_all_children(self) -> Iterable["GroupFile"]:
        """
        Recursively gets all subfiles from itself.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path_name}>"

class GroupDirectory(GroupObject):

    __slots__ = (
        "children",
    )

    name = "directory"

    def __init__(self, path: Path, path_name:str, parent: GroupObject | None, children: Mapping[str, GroupObject]) -> None:
        super().__init__(path, path_name, parent)
        self.children = children

    def get_child(self, child_name:str, trace:Trace) -> tuple["GroupObject|EllipsisType", Errors]:
        if self.children is None or (output := self.children.get(child_name)) is None:
            trace.exception(RuntimeError(f"{self} has no child named {child_name}"))
            return ..., Errors.create_field
        return output, Errors.fine

    def get_all_children(self) -> Iterable["GroupFile"]:
        yield from chain.from_iterable(child.get_all_children() for child in self.children.values())

class GroupFile(GroupObject):

    __slots__ = (
        "domain",
    )

    def __init__(self, path: Path, path_name:str, parent: GroupObject | None, domain:"Domain.Domain") -> None:
        super().__init__(path, path_name, parent)
        self.domain = domain

    def get_all_children(self) -> Iterable["GroupFile"]:
        yield self

class ComponentFile(GroupFile):
    """
    .cmp file
    """

    __slots__ = (
        "group",
    )

    name = ".cmp file"

    def __init__(self, path:Path, path_name:str, parent: GroupObject|None, domain:"Domain.Domain") -> None:
        super().__init__(path, path_name, parent, domain)
        self.group:Group # set by Importer

class ScriptFile(GroupFile):
    """
    .py file
    """

    __slots__ = (
        "module_name",
    )

    name = ".py file"

    def __init__(self, path:Path, path_name:str, parent: GroupObject | None, domain:"Domain.Domain", module_name:str) -> None:
        super().__init__(path, path_name, parent, domain)
        self.module_name = module_name

class Group():
    """
    Basically a file of Fields.
    """

    __slots__ = (
        "domain",
        "error",
        "fields",
        "finals",
        "group_file",
        "name",
        "path",
        "reader",
        "settings",
    )

    def __init__(self, domain:"Domain.Domain", file_path:Path, settings:GroupSettings, fields:Mapping[str,"FieldFactory"], reader:"Reader", error:Errors) -> None:
        self.domain:"Domain.Domain" = domain
        self.path:Path = file_path
        self.name:str = file_path.relative_to(domain.assets_directory).as_posix().removesuffix(file_path.suffix) + "/"
        self.settings:GroupSettings = settings
        self.fields = fields
        self.reader = reader
        self.error = error
        self.group_file:GroupObject
        self.finals:Mapping[str,object]

    @property
    def full_name(self) -> str:
        return f"{self.domain.name}!{self.name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name}!{self.name}>"

    def __hash__(self) -> int:
        return hash((self.domain, self.name))
