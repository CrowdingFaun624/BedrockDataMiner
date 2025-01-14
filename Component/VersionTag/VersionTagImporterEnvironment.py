from pathlib import Path
from typing import Iterable

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.VersionTagComponent as VersionTagComponent
import Version.VersionTag.VersionTag as VersionTag


class VersionTagImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,VersionTag.VersionTag]]):

    assume_type = VersionTagComponent.VersionTagComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.version_tags_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_tags"

    def get_assumed_used_components(self, components: dict[str, VersionTagComponent.VersionTagComponent], name: str) -> Iterable[Component.Component]:
        return (component for component in components.values() if len(component.auto_assigner_field) > 0 or component.is_unreleased_tag)
