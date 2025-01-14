from pathlib import Path
from typing import Iterable

import Component.ImporterEnvironment as ImporterEnvironment
import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent
import Version.VersionFileType as VersionFileType


class VersionFileTypeImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,VersionFileType.VersionFileType]]):

    assume_type = VersionFileTypeComponent.VersionFileTypeComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return [self.domain.version_file_types_file]

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_file_types"
