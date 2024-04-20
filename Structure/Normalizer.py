from typing import Any, Callable, cast, Generic, TYPE_CHECKING, TypeVar

import DataMiners.DataMinerTyping as DataMinerTyping
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier
import Utilities.Version as Version

if TYPE_CHECKING:
    import DataMiners.DataMiner as DataMiner

IN = TypeVar("IN")
OUT = TypeVar("OUT")

class Normalizer(Generic[IN, OUT]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("function", "a Callable", True, Callable),
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))
    )

    def __init__(self, function:Callable[[IN, DataMinerTyping.DependenciesTypedDict], OUT], dependencies:list[str]):
        '''`function` is a Callable that modifies the original object and returns nothing.
        `dependencies` is a list of DataMinerCollection names.'''
        self.type_verifier.base_verify({"function": function, "dependencies": dependencies})

        self.function = function
        self.dependencies = cast(list[DataMinerTyping.DependenciesLiterals], dependencies)

    def __call__(self, data:IN, normalizer_dependencies:"LocalNormalizerDependencies", version_number:int) -> OUT|None:
        if version_number not in (1, 2):
            raise ValueError("`version_number` is not 1 or 2!")
        version = normalizer_dependencies.get_version(version_number)
        this_data:DataMinerTyping.DependenciesTypedDict
        if version is None:
            this_data = cast(DataMinerTyping.DependenciesTypedDict, {dependency: None for dependency in self.dependencies})
        else:
            this_data = cast(DataMinerTyping.DependenciesTypedDict, {dependency: normalizer_dependencies.get_data(version, dependency) for dependency in self.dependencies})
        # `this_data` is only the dataminer data that is needed for this normalizer.
        exception = None
        try:
            return self.function(data, this_data)
        except Exception as e:
            exception = e
            data_string = str(data)
            if len(data_string) > 500:
                exception.args = tuple(list(exception.args) + ["Normalizer excepted!"])
            else:
                exception.args = tuple(list(exception.args) + ["Normalizer excepted at %s on data: %s" % (data_string)])
        if exception is not None:
            raise exception

class NormalizerDependencies():

    def __init__(self, data:dict[tuple[Version.Version, str], Any], dataminer_collections:list["DataMiner.DataMinerCollection"]):
        '''There should only be one data object that is shared between all NormalizerDependencies, or only one NormalizerDependencies object.
        The data is a dictionary of tuples of a version and a dataminer name, and the corresponding data.'''
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict!")
        for index, key in enumerate(data.keys()):
            if not isinstance(key, tuple):
                raise TypeError("Key number %i of `data` is not a tuple, but instead %s!" % (index, key.__class__.__name__))
            if len(key) != 2:
                raise TypeError("Key number %i of `data` is not length 2!" % (index))
            if not isinstance(key[0], Version.Version):
                raise TypeError("Item 0 of key number %i of `data` is not a Version, but instead %s!" % (index, key[0].__class__.__name__))
            if not isinstance(key[1], str):
                raise TypeError("Item 1 of key number %i of `data` is not a str, but instead %s!" % (index, key[1].__class__.__name__))
        if not isinstance(dataminer_collections, list):
            raise TypeError("`dataminer_collections` is not a list!")

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
        if not isinstance(normalizer_dependencies, NormalizerDependencies):
            raise TypeError("`normalizer_dependencies` is not a NormalizerDependencies, but instead a %s!" % (normalizer_dependencies.__class__.__name__))
        if not (version1 is None or isinstance(version1, Version.Version)):
            raise TypeError("`version1` is not a Version or None, but instead a %s!" % (version1.__class__.__name__))
        if not (version2 is None or isinstance(version2, Version.Version)):
            raise TypeError("`version2` is not a Version or None, but instead a %s!" % (version2.__class__.__name__))
        self.parent = normalizer_dependencies
        self.version1 = version1
        self.version2 = version2

    def get_version(self, index:int) -> Version.Version|None:
        match index:
            case 1:
                return self.version1
            case 2:
                return self.version2
            case _:
                raise ValueError("`index` is not 1 or 2!")

    def get_data(self, version:Version.Version, dataminer_name:str) -> Any:
        return self.parent.get_data(version, dataminer_name)

    def __repr__(self) -> str:
        return "<LocalNormalizerDependencies (%s, %s)>" % (str(self.version1), str(self.version2))

class SimpleNormalizerDependencies(LocalNormalizerDependencies):

    def __init__(self, data:DataMinerTyping.DependenciesTypedDict, version:Version.Version):
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict, but instead %s!" % (data.__class__.__name__))
        if not isinstance(version, Version.Version):
            raise TypeError("`version` is not a Version, but instead %s!" % (version.__class__.__name__))

        self.data = data
        self.version = version

    def get_version(self, index: int) -> Version.Version:
        return self.version

    def get_data(self, version:Version.Version, dataminer_name:str) -> Any:
        return self.data[dataminer_name]
