from typing import TypedDict

import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("PacksDataminer",)

class PackTypedDict(TypedDict):
    name: str
    path: str

class PacksDataminer(Dataminer.Dataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", True, str, FileDataminer.location_value_function),
    )

    def initialize(
        self,
        location:str,
    ) -> None:
        self.location = location

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> list[PackTypedDict]:
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
            raise Exceptions.DataminerNothingFoundError(self)
        return packs
