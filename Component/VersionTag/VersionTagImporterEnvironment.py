from pathlib import Path
from typing import Iterable

from Component.Component import Component
from Component.ImporterEnvironment import ImporterEnvironment
from Component.VersionTag.VersionTagComponent import VersionTagComponent
from Utilities.Trace import Trace
from Version.VersionTag.VersionTag import VersionTag


class VersionTagImporterEnvironment(ImporterEnvironment[dict[str,VersionTag]]):

    assume_type = VersionTagComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.version_tags_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_tags"

    def get_assumed_used_components(self, components: dict[str, VersionTagComponent], name: str, trace:Trace) -> Iterable[Component]:
        with trace.enter(self, name, ...):
            return (component for component in components.values() if len(component.auto_assigner_field) > 0 or component.is_unreleased_tag)
        return ()
