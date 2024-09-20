import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Serializer.Serializer as Serializer
import Serializer.JsonSerializer as JsonSerializer
import Utilities.FileManager as FileManager


class SerializerImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,Serializer.Serializer]]):

    assume_type = "Serializer"
    
    def get_component_files(self) -> ImporterEnvironment.Iterable[ImporterEnvironment.Path]:
        return [FileManager.SERIALIZERS_FILE]

    def get_output(self, components: dict[str, Component.Component], name: str) -> tuple[dict[str,Serializer.Serializer], list[Component.Component]]:
        output = super().get_output(components, name)
        output[0]["json_default"] = JsonSerializer.DEFAULT_JSON_SERIALIZER
        return output

    def get_component_group_name(self, file_path: ImporterEnvironment.Path) -> str:
        return "serializers"
