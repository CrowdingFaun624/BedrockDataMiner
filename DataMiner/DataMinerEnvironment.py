from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import DataMiner.DataMiner as DataMiner

a = TypeVar("a")

class DataMinerDependencies():
    "Controls the dependencies of DataMiners."

    def __init__(self, data:dict[str,Any]) -> None:
        '''
        :data: A dictionary with keys of DataMinerCollection names and values of the data they collected for this Version.
        '''
        self.data = data

    def get(self, dataminer_name:str, dataminer:"DataMiner.DataMiner") -> Any:
        '''
        Returns the data associated with the given DataMinerCollection name for this Version, or `default` if the DataMinerCollection exists but has no data for this Version.
        Raises a DataMinerUnregisteredDependencyError if the DataMinerCollection is not listed as a dependency for this DataMiner.
        :dataminer_name: The name of the DataMinerCollection to access.
        :dataminer: The DataMiner attempting to access the dependency.
        '''
        NO_DEFAULT = "NO"
        output:Any|Literal["NO"] = self.get_default(dataminer_name, dataminer, NO_DEFAULT)
        if output is NO_DEFAULT:
            raise Exceptions.DataMinerUnrecognizedDependencyError(dataminer, dataminer_name)
        return cast(Any, output)

    def get_default(self, dataminer_name:str, dataminer:"DataMiner.DataMiner", default:a) -> Any|a:
        '''
        Returns the data associated with the given DataMinerCollection name for this Version, or `default` if the DataMinerCollection exists but has no data for this Version.
        Raises a DataMinerUnregisteredDependencyError if the DataMinerCollection is not listed as a dependency for this DataMiner.
        :dataminer_name: The name of the DataMinerCollection to access.
        :dataminer: The DataMiner attempting to access the dependency.
        :default: The default value to return if the data does not exist for this Version.
        '''
        if dataminer_name not in dataminer.dependencies_str:
            raise Exceptions.DataMinerUnregisteredDependencyError(dataminer, dataminer_name)
        output = self.data.get(dataminer_name, default) # DataMiners cannot output None
        return output

    def set_item(self, name:str, value:Any) -> None:
        if name in self.data:
            raise Exceptions.DataMinerDependencyOverwriteError(self, name)
        self.data[name] = value

    def __repr__(self) -> str:
        return "<%s [%s]>" % (self.__class__.__name__, ", ".join(dependency for dependency in self.data.keys()))

class DataMinerEnvironment():

    def __init__(self, dependency_data:DataMinerDependencies, structure_environment:StructureEnvironment.StructureEnvironment) -> None:
        self.dependency_data = dependency_data
        self.structure_environment = structure_environment
