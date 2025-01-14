from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
import Serializer.Serializer as Serializer
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
import Version.Version as Version
import Version.VersionFileType as VersionFileType
import Version.VersionRange as VersionRange

if TYPE_CHECKING:
    import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
    import Dataminer.Dataminer as Dataminer

class DataminerSettings():

    def __init__(self, kwargs:dict[str,Any], domain:"Domain.Domain") -> None:
        self.arguments = kwargs
        self.domain = domain

        self.version_range:VersionRange.VersionRange
        self.version_file_types:list[VersionFileType.VersionFileType]
        self.version_file_types_str:list[str]|None
        self.file_name:str
        self.name:str
        self.structure:StructureBase.StructureBase
        self.dataminer_class:type["Dataminer.Dataminer"]|None
        self.serializers:dict[str,Serializer.Serializer]
        self.dependencies:list["AbstractDataminerCollection.AbstractDataminerCollection"]

    def link_subcomponents(
        self,
        file_name:str,
        name:str,
        structure:StructureBase.StructureBase,
        dataminer_class:type["Dataminer.Dataminer"]|None,
        serializers:dict[str,Serializer.Serializer],
        dependencies:list["AbstractDataminerCollection.AbstractDataminerCollection"],
        start_version:Version.Version|None,
        end_version:Version.Version|None,
        version_file_types:list[VersionFileType.VersionFileType],
    ) -> list[Exception]:
        self.file_name = file_name
        self.name = name
        self.structure = structure
        self.dataminer_class = dataminer_class
        self.serializers = serializers
        self.dependencies = dependencies
        self.version_range = VersionRange.VersionRange(start_version, end_version)
        self.version_file_types = version_file_types
        self.version_file_types_str = [version_file_type.name for version_file_type in self.version_file_types]
        exceptions:list[Exception] = []
        if dataminer_class is not None and dataminer_class.parameters is not None:
            trace = TypeVerifier.make_trace([self])
            exceptions.extend(dataminer_class.parameters.verify(self.arguments, trace))
        if dataminer_class is not None:
            dataminer_class.manipulate_arguments(self.arguments)
        return exceptions

    def get_dataminer_class(self) -> type["Dataminer.Dataminer"]:
        if self.dataminer_class is None:
            raise Exceptions.AttributeNoneError("dataminer_class", self)
        return self.dataminer_class

    def __repr__(self) -> str:
        if self.name is None:
            return f"<{self.__class__.__name__} id {id(self)}>"
        else:
            version_range = self.version_range
            return f"<DataminerSettings {self.name} \"{str(version_range.start)}\"–\"{str(version_range.stop)}\">"
