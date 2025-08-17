from typing import TYPE_CHECKING, Any, cast

import Utilities.Exceptions as Exceptions
from Structure.StructureEnvironment import PrinterEnvironment, StructureEnvironment
from Structure.StructureInfo import StructureInfo

if TYPE_CHECKING:
    from Dataminer.Dataminer import Dataminer
    from Version.Version import Version

class DataminerDependencies():
    "Controls the dependencies of Dataminers."

    __slots__ = (
        "data",
    )

    def __init__(self, data:dict[str,Any]) -> None:
        '''
        :data: A dictionary with keys of DataminerCollection names and values of the data they collected for this Version.
        '''
        self.data = data

    def get(self, dataminer_name:str, dataminer:"Dataminer") -> Any:
        '''
        Returns the data associated with the given DataminerCollection name for this Version.
        Raises a DataminerUnregisteredDependencyError if the DataminerCollection is not listed as a dependency for this Dataminer.
        :dataminer_name: The name of the DataminerCollection to access.
        :dataminer: The Dataminer attempting to access the dependency.
        '''
        output = self.get_default(dataminer_name, dataminer, ...)
        if output is ...:
            raise Exceptions.DataminerUnrecognizedDependencyError(dataminer, dataminer_name, list(self.data.keys()))
        return cast(Any, output)

    def get_default[a](self, dataminer_name:str, dataminer:"Dataminer", default:a) -> Any|a:
        '''
        Returns the data associated with the given DataminerCollection name for this Version, or `default` if the DataminerCollection exists but has no data for this Version.
        Raises a DataminerUnregisteredDependencyError if the DataminerCollection is not listed as a dependency for this Dataminer.
        :dataminer_name: The name of the DataminerCollection to access.
        :dataminer: The Dataminer attempting to access the dependency.
        :default: The default value to return if the data does not exist for this Version.
        '''
        if not any(dataminer_name == dependency.name for dependency in dataminer.dependencies):
            raise Exceptions.DataminerUnregisteredDependencyError(dataminer, dataminer_name, [dependency.name for dependency in dataminer.dependencies])
        output = self.data.get(dataminer_name, default) # Dataminers cannot output None
        return output

    def has_item(self, dataminer_name:str) -> bool:
        return dataminer_name in self.data

    def set_item(self, name:str, value:Any) -> None:
        if name in self.data:
            raise Exceptions.DataminerDependencyOverwriteError(self, name)
        self.data[name] = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} [{", ".join(dependency for dependency in self.data.keys())}]>"

class DataminerEnvironment():

    __slots__ = (
        "dependency_data",
        "structure_environment",
    )

    def __init__(
        self,
        dependency_data:DataminerDependencies,
        structure_environment:StructureEnvironment,
    ) -> None:
        self.dependency_data = dependency_data
        self.structure_environment = structure_environment

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.dependency_data} {self.structure_environment}>"

    def get_printer_environment(self, version:"Version", structure_info:StructureInfo) -> PrinterEnvironment:
        return PrinterEnvironment(self.structure_environment, structure_info, version, 0)
