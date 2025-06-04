from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
from Structure.StructureBase import StructureBase
from Structure.StructureInfo import StructureInfo
from Utilities.Exceptions import AttributeNoneError
from Utilities.Trace import Trace
from Version.Version import Version
from Version.VersionFileType import VersionFileType
from Version.VersionRange import VersionRange

if TYPE_CHECKING:
    from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
    from Dataminer.Dataminer import Dataminer

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

        self.version_range:VersionRange
        self.version_file_types:list[VersionFileType]
        self.version_file_types_str:list[str]|None
        self.file_name:str
        self.name:str
        self.structure:StructureBase
        self.dataminer_class:type["Dataminer"]|None
        self.dependencies:list["AbstractDataminerCollection"]
        self.structure_info: StructureInfo

    def link_subcomponents(
        self,
        trace:Trace,
        file_name:str,
        name:str,
        structure:StructureBase,
        dataminer_class:type["Dataminer"]|None,
        dependencies:list["AbstractDataminerCollection"],
        start_version:Version|None,
        end_version:Version|None,
        structure_info:StructureInfo,
        version_file_types:list[VersionFileType],
    ) -> None:
        with trace.enter(self, name, ...):
            self.file_name = file_name
            self.name = name
            self.structure = structure
            self.dataminer_class = dataminer_class
            self.dependencies = dependencies
            self.version_range = VersionRange(start_version, end_version)
            self.structure_info = structure_info
            self.version_file_types = version_file_types
            self.version_file_types_str = [version_file_type.name for version_file_type in self.version_file_types]
            if dataminer_class is not None and dataminer_class.parameters is not None:
                dataminer_class.parameters.verify(self.arguments, trace)
            if dataminer_class is not None:
                dataminer_class.manipulate_arguments(self.arguments)

    def get_dataminer_class(self) -> type["Dataminer"]:
        if self.dataminer_class is None:
            raise AttributeNoneError("dataminer_class", self)
        return self.dataminer_class

    def __repr__(self) -> str:
        if self.name is None:
            return f"<{self.__class__.__name__} id {id(self)}>"
        else:
            version_range = self.version_range
            return f"<DataminerSettings {self.name} \"{str(version_range.start)}\"–\"{str(version_range.stop)}\">"
