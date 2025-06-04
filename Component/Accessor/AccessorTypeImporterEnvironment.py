from pathlib import Path
from typing import Iterable

from Component.Accessor.AccessorTypeComponent import AccessorTypeComponent
from Component.ImporterEnvironment import ImporterEnvironment
from Downloader.AccessorType import AccessorType


class AccessorTypeImporterEnvironment(ImporterEnvironment[dict[str,AccessorType]]):

    assume_type = AccessorTypeComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.accessor_types_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "accessor_types"
