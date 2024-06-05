from typing import TYPE_CHECKING, Any, TypeVar, overload

import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import DataMiners.DataMiner as DataMiner

a = TypeVar("a")
NO_DEFAULT = "NO"

class DataMinerDependencies():
    "Controls the dependencies of DataMiners."
    
    def __init__(self, data:dict[str,Any]) -> None:
        '''
        :data: A dictionary with keys of DataMinerCollection names and values of the data they collected for this Version.
        '''
        self.data = data
    
    @overload
    def get(self, dataminer_name:str, dataminer:"DataMiner.DataMiner") -> Any:
        '''
        Returns the data associated with the given DataMinerCollection name for this Version.
        Raises a DataMinerUnregisteredDependencyError if the DataMinerCollection is not listed as a dependency for this DataMiner.
        Raises a DataMinerUnrecognizedDependencyError if the DataMinerCollection exists but has no data for this Version.
        :dataminer_name: The name of the DataMinerCollection to access.
        :dataminer: The DataMiner attempting to access the dependency.
        '''
    @overload
    def get(self, dataminer_name:str, dataminer:"DataMiner.DataMiner", default:a) -> Any|a:
        '''
        Returns the data associated with the given DataMinerCollection name for this Version, or `default` if the DataMinerCollection exists but has no data for this Version.
        Raises a DataMinerUnregisteredDependencyError if the DataMinerCollection is not listed as a dependency for this DataMiner.
        :dataminer_name: The name of the DataMinerCollection to access.
        :dataminer: The DataMiner attempting to access the dependency.
        :default: The default value to return if the data does not exist for this Version.
        '''
    def get(self, dataminer_name:str, dataminer:"DataMiner.DataMiner", default:a=NO_DEFAULT) -> Any|a:
        if dataminer_name not in dataminer.dependencies:
            raise Exceptions.DataMinerUnregisteredDependencyError(dataminer, dataminer_name)
        output = self.data.get(dataminer_name, default) # DataMiners cannot output None
        if output is NO_DEFAULT:
            raise Exceptions.DataMinerUnrecognizedDependencyError(dataminer, dataminer_name)
        return output

class DataMinerEnvironment():

    def __init__(self, dependency_data:DataMinerDependencies, structure_environment:StructureEnvironment.StructureEnvironment) -> None:
        self.dependency_data = dependency_data
        self.structure_environment = structure_environment
