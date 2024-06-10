from typing import TYPE_CHECKING, Any

import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Version.Version as Version
import Version.VersionParser as VersionParser
import Version.VersionRange as VersionRange

if TYPE_CHECKING:
    import DataMiner.DataMiner as DataMiner
    import DataMiner.DataMinerCollection as DataMinerCollection

def str_to_version(version_str:str|None) -> Version.Version|None:
    if version_str is None: return None
    versions = VersionParser.versions
    output = versions.get(version_str)
    if output is None:
        raise Exceptions.UnrecognizedVersionError(version_str)
    return output

class DataMinerSettings():

    def __init__(self, start_version_str:str|None, end_version_str:str|None, files:list[str], kwargs:dict[str,Any]) -> None:

        self.version_range = VersionRange.VersionRange(str_to_version(start_version_str), str_to_version(end_version_str))
        self.files = files
        self.kwargs = kwargs

        self.file_name:str|None = None
        self.name:str|None = None
        self.structure:StructureBase.StructureBase|None = None
        self.dataminer_class:type["DataMiner.DataMiner"]|None = None
        self.dependencies:list["DataMinerCollection.DataMinerCollection"]|None = None

    def link_subcomponents(self, file_name:str, name:str, structure:StructureBase.StructureBase, dataminer_class:type["DataMiner.DataMiner"]|None, dependencies:list["DataMinerCollection.DataMinerCollection"]) -> None:
        self.file_name = file_name
        self.name = name
        self.structure = structure
        self.dataminer_class = dataminer_class
        self.dependencies = dependencies

    def get_dependencies(self) -> list["DataMinerCollection.DataMinerCollection"]:
        if self.dependencies is None:
            raise Exceptions.AttributeNoneError("dependencies", self)
        return self.dependencies

    def get_dataminer_class(self) -> type["DataMiner.DataMiner"]:
        if self.dataminer_class is None:
            raise Exceptions.AttributeNoneError("dataminer_class", self)
        return self.dataminer_class

    def get_name(self) -> str:
        '''
        Get the name of this DataMinerSettings, and raise an exception if it is None.
        '''
        if self.name is None:
            raise Exceptions.AttributeNoneError("name", self)
        return self.name

    def get_file_name(self) -> str:
        '''
        Get the file name of this DataMinerSettings, and raise an exception if it is None.
        '''
        if self.file_name is None:
            raise Exceptions.AttributeNoneError("file_name", self)
        return self.file_name

    def __repr__(self) -> str:
        if self.name is None:
            return "<DataMinerSettings \"%s\"–\"%s\">" % (str(self.version_range.start), str(self.version_range.stop))
        else:
            return "<DataMinerSettings %s \"%s\"–\"%s\">" % (self.name, str(self.version_range.start), str(self.version_range.stop))
