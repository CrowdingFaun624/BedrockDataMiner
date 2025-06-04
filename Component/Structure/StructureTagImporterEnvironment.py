from pathlib import Path
from typing import Iterable

from Component.ImporterEnvironment import ImporterEnvironment
from Structure.StructureTag import StructureTag


class StructureTagImporterEnvironment(ImporterEnvironment[dict[str,StructureTag]]):

    assume_type = "StructureTag"

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.structure_tags_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "structure_tags"
