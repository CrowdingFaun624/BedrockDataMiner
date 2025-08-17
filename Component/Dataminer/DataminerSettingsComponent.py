from typing import Any, Mapping, NotRequired, Required, Sequence, TypedDict

from Component.Component import Component
from Component.Scripts import Script
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerSettings import DataminerSettings
from Structure.StructureInfo import StructureInfo
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    ScriptTypeVerifier,
    SubclassTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)
from Version.Version import Version
from Version.VersionFileType import VersionFileType
from Version.VersionRange import VersionRange


class DataminerSettingsTypedDict(TypedDict):
    arguments: NotRequired[Mapping[str,Any]]
    dependencies: NotRequired[AbstractDataminerCollection | Sequence[AbstractDataminerCollection]]
    files: NotRequired[VersionFileType | Sequence[VersionFileType]]
    name: Required[Script[type[Dataminer]] | None]
    new: Required[Version | None]
    old: Required[Version | None]
    optional_dependencies: NotRequired[AbstractDataminerCollection | Sequence[AbstractDataminerCollection]]
    structure_info: NotRequired[Mapping[str, Any]]

def convert_to_sequence[T](data:T|Sequence[T], item_type:type[T]) -> Sequence[T]:
    return [data] if isinstance(data, item_type) else data # type: ignore

class DataminerSettingsComponent(Component[DataminerSettings, DataminerSettingsTypedDict]):

    type_name = "DataminerSettings"
    object_type = DataminerSettings
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("dependencies", False, UnionTypeVerifier(AbstractDataminerCollection, ListTypeVerifier(AbstractDataminerCollection, list))),
        TypedDictKeyTypeVerifier("files", False, UnionTypeVerifier(VersionFileType, ListTypeVerifier(VersionFileType, list))),
        TypedDictKeyTypeVerifier("name", True, UnionTypeVerifier(type(None), ScriptTypeVerifier(SubclassTypeVerifier(Dataminer)))),
        TypedDictKeyTypeVerifier("new", True, (type(None), Version)),
        TypedDictKeyTypeVerifier("old", True, (type(None), Version)),
        TypedDictKeyTypeVerifier("optional_dependencies", False, UnionTypeVerifier(AbstractDataminerCollection, ListTypeVerifier(AbstractDataminerCollection, list))),
        TypedDictKeyTypeVerifier("structure_info", False, DictTypeVerifier(dict, str, object)),
    ))

    def check(self, fields: DataminerSettingsTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        if (dataminer_class := fields["name"]) is not None and dataminer_class.object.parameters is not None:
            return dataminer_class.object.parameters.verify(fields.get("arguments", {}), trace)
        else:
            return False

    def link_final(self, fields: DataminerSettingsTypedDict) -> None:
        super().link_final(fields)
        self.final.link_dataminer_settings(
            arguments=fields.get("arguments", {}),
            dataminer_class=None if (dataminer_script := fields["name"]) is None else dataminer_script.object,
            dependencies=convert_to_sequence(fields.get("dependencies", []), AbstractDataminerCollection),
            optional_dependencies=convert_to_sequence(fields.get("optional_dependencies", []), AbstractDataminerCollection),
            structure_info=StructureInfo(fields.get("structure_info", {}), self.group.domain, self.full_name),
            version_file_types=convert_to_sequence(fields.get("files", []), VersionFileType),
            version_range=VersionRange(fields["old"], fields["new"]),
        )
