from typing import (TYPE_CHECKING, Any, Callable, Generic, Literal, TypeVar,
                    cast)

import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Version.Version as Version

if TYPE_CHECKING:
    import DataMiner.DataMinerCollection as DataMinerCollection

IN = TypeVar("IN")
OUT = TypeVar("OUT")

class Normalizer(Generic[IN, OUT]):
    '''Changes data before a Structure looks at it.'''

    def __init__(self, function:Callable[[IN, DataMinerTyping.DependenciesTypedDict], OUT], dependencies:list[str]):
        '''
        :function: A Callable that modifies the original object and returns nothing.
        :dependencies: A list of DataMinerCollection names.
        '''

        self.function = function
        self.dependencies = cast(list[DataMinerTyping.DependenciesLiterals], dependencies)

    def __call__(self, data:IN, normalizer_dependencies:"LocalNormalizerDependencies", version_number:Literal[1,2]) -> OUT|None:
        '''
        Activates the Normalizer.
        :data: The argument of the Normalizer's function.
        :normalizer_dependencies: The LocalNormalizerDependencies containing other data files this Normalizer depends on.
        :version_number: Integer describing if the first Version or second Version of the normalizer dependencies is used.
        '''
        version = normalizer_dependencies.get_version(version_number)
        this_data:DataMinerTyping.DependenciesTypedDict
        if version is None:
            this_data = cast(DataMinerTyping.DependenciesTypedDict, {dependency: None for dependency in self.dependencies})
        else:
            this_data = cast(DataMinerTyping.DependenciesTypedDict, {dependency: normalizer_dependencies.get_data(version, dependency) for dependency in self.dependencies})
        # `this_data` is only the dataminer data that is needed for this normalizer.
        try:
            return self.function(data, this_data)
        except Exception:
            raise Exceptions.NormalizerError(self, data)

class NormalizerDependencies():

    def __init__(self, data:dict[tuple[Version.Version, str], Any], dataminer_collections:list["DataMinerCollection.DataMinerCollection"]):
        '''There should only be one data object that is shared between all NormalizerDependencies, or only one NormalizerDependencies object.
        The data is a dictionary of tuples of a version and a dataminer name, and the corresponding data.'''
        self.data = data
        self.dataminer_collections = {dataminer_collection.name: dataminer_collection for dataminer_collection in dataminer_collections}

    def get_data(self, version:Version.Version, dataminer_name:str) -> Any:
        if (version, dataminer_name) not in self.data:
            self.data[version, dataminer_name] = self.dataminer_collections[dataminer_name].get_data_file(version, non_exist_ok=True)
        return self.data[version, dataminer_name]

    def forget(self, version:Version.Version) -> None:
        '''Removes everything related to the given version from the data.'''
        items_to_delete:list[tuple[Version.Version,str]] = []
        for data_version, data_miner in self.data.keys():
            if data_version is version:
                items_to_delete.append((data_version, data_miner))
        for item_to_delete in items_to_delete:
            del self.data[item_to_delete]

class LocalNormalizerDependencies():

    def __init__(self, normalizer_dependencies:NormalizerDependencies, version1:Version.Version|None, version2:Version.Version|None):
        self.parent = normalizer_dependencies
        self.version1 = version1
        self.version2 = version2

    def get_version(self, index:Literal[1,2]) -> Version.Version|None:
        match index:
            case 1:
                return self.version1
            case 2:
                return self.version2

    def get_data(self, version:Version.Version, dataminer_name:str) -> Any:
        return self.parent.get_data(version, dataminer_name)

    def __repr__(self) -> str:
        return "<%s (%s, %s)>" % (self.__class__.__name__, str(self.version1), str(self.version2))

class NullNormalizerDependencies(LocalNormalizerDependencies):
    '''Does not actually contain any normalizer dependencies, and raises an exception if you try to do anything with it.'''
    def __init__(self):
        self.parent = None
        self.version1 = None
        self.version2 = None

    def get_data(self, version: Version.Version, dataminer_name: str) -> Any:
        raise Exceptions.NullNormalizerDependenciesAccessorError(self, version, dataminer_name)

    def __repr__(self) -> str:
        return "<%s>" % (self.__class__.__name__)

class SimpleNormalizerDependencies(LocalNormalizerDependencies):

    def __init__(self, data:DataMinerTyping.DependenciesTypedDict, version:Version.Version):
        self.data = data
        self.version = version

    def get_version(self, index: Literal[1,2]) -> Version.Version:
        return self.version

    def get_data(self, version:Version.Version, dataminer_name:str) -> Any:
        return self.data[dataminer_name]
