from typing import TypedDict

from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import location_value_function
from Utilities.Exceptions import DataminerNothingFoundError
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

__all__ = ("PacksDataminer",)

class PackTypedDict(TypedDict):
    name: str
    path: str

class PacksDataminer(Dataminer):

    __slots__ = (
        "location",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, str, location_value_function),
    )

    def initialize(
        self,
        location:str,
    ) -> None:
        self.location = location

    def activate(self, environment:DataminerEnvironment) -> list[PackTypedDict]:
        dependencies = self.dependencies
        assert len(self.dependencies) == 1
        file_list:dict[str,str] = environment.dependency_data.get(dependencies[0].name, self)
        packs:list[PackTypedDict] = []
        pack_names:set[str] = set()
        for file in file_list:
            if not file.startswith(self.location):
                continue
            name = file.removeprefix(self.location).split("/", maxsplit=1)[0]
            if file.count("/") == 1 or name == "" or name in pack_names:
                continue
            pack_names.add(name)
            packs.append({"name": name, "path": f"{self.location}{name}/"})
        if len(packs) == 0:
            raise DataminerNothingFoundError(self)
        return packs
