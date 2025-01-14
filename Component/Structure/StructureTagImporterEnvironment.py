import Component.ImporterEnvironment as ImporterEnvironment
import Structure.StructureTag as StructureTag


class StructureTagImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,StructureTag.StructureTag]]):

    assume_type = "StructureTag"

    __slots__ = ()

    def get_component_files(self) -> ImporterEnvironment.Iterable[ImporterEnvironment.Path]:
        return (self.domain.structure_tags_file,)

    def get_component_group_name(self, file_path: ImporterEnvironment.Path) -> str:
        return "structure_tags"
