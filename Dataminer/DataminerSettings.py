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
        "full_name",
        "name",
        "structure",
        "structure_info",
        "version_file_types",
        "version_range",
    )

    def __init__(self, full_name:str, kwargs:dict[str,Any], domain:"Domain.Domain") -> None:
        self.full_name = full_name
        self.arguments = kwargs
        self.domain = domain

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
            self.file_name:str = file_name
            self.name:str = name
            self.structure:StructureBase = structure
            self.dataminer_class:type["Dataminer"]|None = dataminer_class
            self.dependencies:list["AbstractDataminerCollection"] = dependencies
            self.version_range:VersionRange = VersionRange(start_version, end_version)
            self.structure_info:StructureInfo = structure_info
            self.version_file_types:list[VersionFileType] = version_file_types
            if dataminer_class is not None and dataminer_class.parameters is not None:
                dataminer_class.parameters.verify(self.arguments, trace)
            if dataminer_class is not None:
                dataminer_class.manipulate_arguments(self.arguments)

    def get_dataminer_class(self) -> type["Dataminer"]:
        if self.dataminer_class is None:
            raise AttributeNoneError("dataminer_class", self)
        return self.dataminer_class

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name} \"{str(self.version_range.start)}\"–\"{str(self.version_range.stop)}\">"
