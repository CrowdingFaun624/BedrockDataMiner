from typing import TYPE_CHECKING, Any, Mapping, Sequence

from Component.ComponentObject import ComponentObject
from Structure.StructureInfo import StructureInfo
from Version.VersionFileType import VersionFileType
from Version.VersionRange import VersionRange

if TYPE_CHECKING:
    from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
    from Dataminer.Dataminer import Dataminer

class DataminerSettings(ComponentObject):

    __slots__ = (
        "arguments",
        "dataminer_class",
        "dependencies",
        "optional_dependencies",
        "structure",
        "structure_info",
        "version_file_types",
        "version_range",
    )

    def link_dataminer_settings(
        self,
        arguments:Mapping[Any,Any],
        dataminer_class:type["Dataminer"]|None,
        dependencies:Sequence["AbstractDataminerCollection"],
        optional_dependencies:Sequence["AbstractDataminerCollection"],
        structure_info:StructureInfo,
        version_file_types:Sequence[VersionFileType],
        version_range:VersionRange,
    ) -> None:
        self.arguments = arguments
        self.dataminer_class:type["Dataminer"]|None = dataminer_class
        self.dependencies:Sequence["AbstractDataminerCollection"] = dependencies
        self.optional_dependencies:Sequence["AbstractDataminerCollection"] = optional_dependencies
        self.version_range:VersionRange = version_range
        self.structure_info:StructureInfo = structure_info
        self.version_file_types:Sequence[VersionFileType] = version_file_types

    def get_dataminer_class(self) -> type["Dataminer"]|None:
        return self.dataminer_class

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name} \"{str(self.version_range.start)}\"–\"{str(self.version_range.stop)}\">"
