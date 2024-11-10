import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Structure.StructureTag as StructureTag
import Utilities.FileManager as FileManager


class StructureTagImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,StructureTag.StructureTag]]):

    assume_type = "StructureTag"
    
    def get_component_files(self) -> ImporterEnvironment.Iterable[ImporterEnvironment.Path]:
        return [FileManager.STRUCTURE_TAGS_FILE]

    def get_output(self, components: dict[str, Component.Component], name: str) -> dict[str,StructureTag.StructureTag]:
        output = super().get_output(components, name)
        return output

    def get_component_group_name(self, file_path: ImporterEnvironment.Path) -> str:
        return "structure_tags"
