from typing import TYPE_CHECKING, Any

import Serializer.Serializer as Serializer
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version
import Version.VersionFileType as VersionFileType
import Version.VersionRange as VersionRange

if TYPE_CHECKING:
    import DataMiner.DataMiner as DataMiner
    import DataMiner.DataMinerCollection as DataMinerCollection

class DataMinerSettings():

    def __init__(self, kwargs:dict[str,Any]) -> None:

        self.version_range:VersionRange.VersionRange|None = None
        self.version_file_types:list[VersionFileType.VersionFileType]|None = None
        self.version_file_types_str:list[str]|None = None
        self.arguments = kwargs

        self.file_name:str|None = None
        self.name:str|None = None
        self.structure:StructureBase.StructureBase|None = None
        self.dataminer_class:type["DataMiner.DataMiner"]|None = None
        self.serializer:Serializer.Serializer|None = None
        self.dependencies:list["DataMinerCollection.DataMinerCollection"]|None = None

    def link_subcomponents(
        self,
        file_name:str,
        name:str,
        structure:StructureBase.StructureBase,
        dataminer_class:type["DataMiner.DataMiner"]|None,
        serializer:Serializer.Serializer|None,
        dependencies:list["DataMinerCollection.DataMinerCollection"],
        start_version:Version.Version|None,
        end_version:Version.Version|None,
        version_file_types:list[VersionFileType.VersionFileType],
    ) -> list[Exception]:
        self.file_name = file_name
        self.name = name
        self.structure = structure
        self.dataminer_class = dataminer_class
        self.serializer = serializer
        self.dependencies = dependencies
        self.version_range = VersionRange.VersionRange(start_version, end_version)
        self.version_file_types = version_file_types
        self.version_file_types_str = [version_file_type.name for version_file_type in self.version_file_types]
        exceptions:list[Exception] = []
        if dataminer_class is not None and dataminer_class.parameters is not None:
            trace = TypeVerifier.make_trace([self])
            exceptions.extend(dataminer_class.parameters.verify(self.arguments, trace))
        if dataminer_class is not None and self.serializer is None and dataminer_class.requires_serializer:
            exceptions.append(Exceptions.DataMinerSerializerMissingError(self, dataminer_class))
        if dataminer_class is not None:
            dataminer_class.manipulate_arguments(self.arguments)
        return exceptions

    def get_version_range(self) -> VersionRange.VersionRange:
        if self.version_range is None:
            raise Exceptions.AttributeNoneError("version_range", self)
        return self.version_range

    def get_version_file_types(self) -> list[VersionFileType.VersionFileType]:
        if self.version_file_types is None:
            raise Exceptions.AttributeNoneError("version_file_types", self)
        return self.version_file_types

    def get_files_str(self) -> list[str]:
        if self.version_file_types_str is None:
            raise Exceptions.AttributeNoneError("version_file_types_str", self)
        return self.version_file_types_str

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
            return "<DataMinerSettings id %i>" % (id(self),)
        else:
            version_range = self.get_version_range()
            return "<DataMinerSettings %s \"%s\"–\"%s\">" % (self.get_name(), str(version_range.start), str(version_range.stop))
