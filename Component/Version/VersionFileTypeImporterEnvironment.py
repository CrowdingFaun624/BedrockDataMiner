from pathlib import Path
from typing import Iterable

from Component.ImporterEnvironment import ImporterEnvironment
from Component.Version.VersionFileTypeComponent import VersionFileTypeComponent
from Version.VersionFileType import VersionFileType


class VersionFileTypeImporterEnvironment(ImporterEnvironment[dict[str,VersionFileType]]):

    assume_type = VersionFileTypeComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.version_file_types_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_file_types"
