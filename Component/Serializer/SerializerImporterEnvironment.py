import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Serializer.Serializer as Serializer
import Utilities.FileManager as FileManager


class SerializerImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,Serializer.Serializer]]):

    assume_type = "Serializer"
    
    def get_component_files(self) -> ImporterEnvironment.Iterable[ImporterEnvironment.Path]:
        return [FileManager.SERIALIZERS_FILE]

    def get_output(self, components: dict[str, Component.Component], name: str) -> dict[str,Serializer.Serializer]:
        output = super().get_output(components, name)
        return output

    def get_assumed_used_components(self, components:dict[str,Component.Component], name:str) -> ImporterEnvironment.Iterable[Component.Component]:
        # Serializers can be referenced in random data files or by string-y reference in other Serializers
        return components.values()

    def get_component_group_name(self, file_path: ImporterEnvironment.Path) -> str:
        return "serializers"
