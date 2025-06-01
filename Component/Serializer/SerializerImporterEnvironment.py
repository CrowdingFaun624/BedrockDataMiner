import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Serializer.Serializer as Serializer
import Utilities.Trace as Trace


class SerializerImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,Serializer.Serializer]]):

    assume_type = "Serializer"

    __slots__ = ()

    def get_component_files(self) -> ImporterEnvironment.Iterable[ImporterEnvironment.Path]:
        return (self.domain.serializers_file,)

    def get_assumed_used_components(self, components:dict[str,Component.Component], name:str, trace:Trace.Trace) -> ImporterEnvironment.Iterable[Component.Component]:
        # Serializers can be referenced in random data files or by string-y reference in other Serializers
        with trace.enter(self, name, ...):
            return components.values()
        return ()

    def get_component_group_name(self, file_path: ImporterEnvironment.Path) -> str:
        return "serializers"
