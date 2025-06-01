from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
import Structure.StructureBase as StructureBase
import Structure.StructureInfo as StructureInfo
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Version.Version as Version
import Version.VersionFileType as VersionFileType
import Version.VersionRange as VersionRange

if TYPE_CHECKING:
    import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
    import Dataminer.Dataminer as Dataminer

class DataminerSettings():

    __slots__ = (
        "arguments",
        "dataminer_class",
        "dependencies",
        "domain",
        "file_name",
        "name",
        "structure",
        "structure_info",
        "version_file_types",
        "version_file_types_str",
        "version_range",
    )

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
        self.dependencies:list["AbstractDataminerCollection.AbstractDataminerCollection"]
        self.structure_info: StructureInfo.StructureInfo

    def link_subcomponents(
        self,
        trace:Trace.Trace,
        file_name:str,
        name:str,
        structure:StructureBase.StructureBase,
        dataminer_class:type["Dataminer.Dataminer"]|None,
        dependencies:list["AbstractDataminerCollection.AbstractDataminerCollection"],
        start_version:Version.Version|None,
        end_version:Version.Version|None,
        structure_info:StructureInfo.StructureInfo,
        version_file_types:list[VersionFileType.VersionFileType],
    ) -> None:
        with trace.enter(self, name, ...):
            self.file_name = file_name
            self.name = name
            self.structure = structure
            self.dataminer_class = dataminer_class
            self.dependencies = dependencies
            self.version_range = VersionRange.VersionRange(start_version, end_version)
            self.structure_info = structure_info
            self.version_file_types = version_file_types
            self.version_file_types_str = [version_file_type.name for version_file_type in self.version_file_types]
            if dataminer_class is not None and dataminer_class.parameters is not None:
                dataminer_class.parameters.verify(self.arguments, trace)
            if dataminer_class is not None:
                dataminer_class.manipulate_arguments(self.arguments)

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
