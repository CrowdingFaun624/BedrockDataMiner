from pathlib import Path
from typing import Iterable

from Component.Component import Component
from Component.ImporterEnvironment import ImporterEnvironment
from Serializer.Serializer import Serializer
from Utilities.Trace import Trace


class SerializerImporterEnvironment(ImporterEnvironment[dict[str,Serializer]]):

    assume_type = "Serializer"

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.serializers_file,)

    def get_assumed_used_components(self, components:dict[str,Component], name:str, trace:Trace) -> Iterable[Component]:
        # Serializers can be referenced in random data files or by string-y reference in other Serializers
        with trace.enter(self, name, ...):
            return components.values()
        return ()

    def get_component_group_name(self, file_path: Path) -> str:
        return "serializers"
