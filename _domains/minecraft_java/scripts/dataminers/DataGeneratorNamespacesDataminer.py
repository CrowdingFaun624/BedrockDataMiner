from typing import AbstractSet, Iterable, Sequence, TypedDict

from Component.ComponentFunctions import component_function
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import location_value_function
from Utilities.Exceptions import DataminerNothingFoundError
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class PackTypedDict(TypedDict):
    name: str

class OutputTypedDict(TypedDict):
    packs: dict[str,PackTypedDict]
    namespaces: dict[str,PackTypedDict]

@component_function()
class DataGeneratorNamespacesDataminer(Dataminer):

    __slots__ = (
        "ignore",
        "subdirectory",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("ignore", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("subdirectory", True, str, function=location_value_function),
    )

    def initialize(
        self,
        ignore:Sequence[str],
        subdirectory:str,
    ) -> None:
        self.ignore:AbstractSet[str] = set(ignore)
        self.subdirectory = subdirectory

    def activate(self, environment:DataminerEnvironment) -> OutputTypedDict:
        dependencies = self.dependencies
        assert len(self.dependencies) == 1
        file_list:Iterable[str] = environment.dependency_data.get(dependencies[0].name, self)
        namespaces:list[str] = []
        already_namespaces:set[str] = set()
        for file in file_list:
            if not file.startswith(self.subdirectory): continue
            split_file:Sequence[str] = file.removeprefix(self.subdirectory).split("/", maxsplit=1)
            if len(split_file) < 2: continue
            namespace_name:str = split_file[0]
            if namespace_name in self.ignore or namespace_name in already_namespaces: continue
            already_namespaces.add(namespace_name)
            namespaces.append(namespace_name)
        if len(namespaces) == 0:
            raise DataminerNothingFoundError(self)
        return {"packs": {"": {"name": ""}}, "namespaces": {f"{self.subdirectory}{namespace}/": {"name": namespace} for namespace in namespaces}}
