from typing import TYPE_CHECKING, Any, cast

import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Dataminer.Dataminer as Dataminer
    import Version.Version as Version

class DataminerDependencies():
    "Controls the dependencies of Dataminers."

    def __init__(self, data:dict[str,Any]) -> None:
        '''
        :data: A dictionary with keys of DataminerCollection names and values of the data they collected for this Version.
        '''
        self.data = data

    def get(self, dataminer_name:str, dataminer:"Dataminer.Dataminer") -> Any:
        '''
        Returns the data associated with the given DataminerCollection name for this Version.
        Raises a DataminerUnregisteredDependencyError if the DataminerCollection is not listed as a dependency for this Dataminer.
        :dataminer_name: The name of the DataminerCollection to access.
        :dataminer: The Dataminer attempting to access the dependency.
        '''
        output = self.get_default(dataminer_name, dataminer, ...)
        if output is ...:
            raise Exceptions.DataminerUnrecognizedDependencyError(dataminer, dataminer_name)
        return cast(Any, output)

    def get_default[a](self, dataminer_name:str, dataminer:"Dataminer.Dataminer", default:a) -> Any|a:
        '''
        Returns the data associated with the given DataminerCollection name for this Version, or `default` if the DataminerCollection exists but has no data for this Version.
        Raises a DataminerUnregisteredDependencyError if the DataminerCollection is not listed as a dependency for this Dataminer.
        :dataminer_name: The name of the DataminerCollection to access.
        :dataminer: The Dataminer attempting to access the dependency.
        :default: The default value to return if the data does not exist for this Version.
        '''
        if dataminer_name not in dataminer.dependencies_str:
            raise Exceptions.DataminerUnregisteredDependencyError(dataminer, dataminer_name)
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

    def __init__(self, dependency_data:DataminerDependencies, structure_environment:StructureEnvironment.StructureEnvironment) -> None:
        self.dependency_data = dependency_data
        self.structure_environment = structure_environment

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.dependency_data} {self.structure_environment}>"

    def get_printer_environment(self, version:"Version.Version") -> StructureEnvironment.PrinterEnvironment:
        return StructureEnvironment.PrinterEnvironment(self.structure_environment, None, version, 0)
