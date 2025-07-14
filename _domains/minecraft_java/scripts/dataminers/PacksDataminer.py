from typing import Iterable, TypedDict

from Component.ComponentFunctions import component_function
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import location_value_function
from Utilities.Exceptions import DataminerNothingFoundError
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class PackTypedDict(TypedDict):
    name: str

class OutputTypedDict(TypedDict):
    packs: dict[str,PackTypedDict]
    namespaces: dict[str,PackTypedDict]

@component_function()
class PacksDataminer(Dataminer):

    __slots__ = (
        "namespace_location",
        "subpack_location",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("namespace_location", True, str, location_value_function),
        TypedDictKeyTypeVerifier("subpack_location", False, str, location_value_function),
    )

    def initialize(
        self,
        namespace_location:str,
        subpack_location:str|None=None
    ) -> None:
        self.namespace_location = namespace_location
        self.subpack_location:str|None = subpack_location

    def activate(self, environment:DataminerEnvironment) -> OutputTypedDict:
        dependencies = self.dependencies
        assert len(self.dependencies) == 1
        file_list:Iterable[str] = environment.dependency_data.get(dependencies[0].name, self) # generator so that iteration can stop and start.
        packs:dict[str,PackTypedDict] = {}
        namespaces:dict[str,PackTypedDict] = {}
        for file in file_list:
            self.process_pack("", "", file, packs, namespaces, environment)
        if len(packs) == 0:
            raise DataminerNothingFoundError(self)
        return {"packs": packs, "namespaces": namespaces}

    def process_pack(self, pack_name:str, pack_path:str, file:str, packs:dict[str,PackTypedDict], namespaces:dict[str,PackTypedDict], environment:DataminerEnvironment) -> None:
        # this method is responsible for adding the pack to the pack list and adding namespaces.
        if pack_path not in packs:
            pack:PackTypedDict = {"name": pack_name}
            packs[pack_path] = pack
        namespace_directory = pack_path + self.namespace_location
        if file.startswith(namespace_directory):
            namespace_name = file.removeprefix(namespace_directory).split("/", maxsplit=1)[0]
            namespace_path = namespace_directory + namespace_name + "/"
            self.process_namespace(namespace_name, namespace_path, file, packs, namespaces, environment)

    def process_namespace(self, namespace_name:str, namespace_path:str, file:str, packs:dict[str,PackTypedDict], namespaces:dict[str,PackTypedDict], environment:DataminerEnvironment) -> None:
        if namespace_name == ".mcassetsroot":
            return
        if namespace_path not in namespaces:
            namespace:PackTypedDict = {"name": namespace_name}
            namespaces[namespace_path] = namespace
        if self.subpack_location is None:
            return
        pack_directory = namespace_path + self.subpack_location
        if file.startswith(pack_directory):
            pack_name = file.removeprefix(pack_directory).split("/", maxsplit=1)[0]
            pack_path = pack_directory + pack_name + "/"
            self.process_pack(pack_name, pack_path, file, packs, namespaces, environment)
