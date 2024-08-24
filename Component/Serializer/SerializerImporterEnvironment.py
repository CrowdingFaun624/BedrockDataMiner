import Component.ImporterEnvironment as ImporterEnvironment
import Utilities.FileManager as FileManager


class SerializerImporterEnvironment(ImporterEnvironment.ImporterEnvironment):

    assume_type = "Serializer"
    
    def get_component_files(self) -> ImporterEnvironment.Iterable[ImporterEnvironment.Path]:
        return [FileManager.SERIALIZERS_FILE]

    def get_component_group_name(self, file_path: ImporterEnvironment.Path) -> str:
        return "serializers"
