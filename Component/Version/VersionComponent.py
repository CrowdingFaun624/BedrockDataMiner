import datetime
from typing import Any

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Version.Field.OptionalVersionField as OptionalVersionField
import Component.Version.Field.VersionFileListField as VersionFileListField
import Component.Version.Field.VersionTagListField as VersionTagListField
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version


class VersionComponent(Component.Component[Version.Version]):

    class_name = "Version"
    class_name_article = "a Version"
    my_capabilities = Capabilities.Capabilities(is_version=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("files", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.DictTypeVerifier(dict, str, object, "a dict", "a str", "an object"), "a dict", "a str", "a dict"), "a dict", "a str", "a dict")),
        TypeVerifier.TypedDictKeyTypeVerifier("parent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("time", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    @classmethod
    def normalize_files(cls, files:dict[str,dict[str,Any]]) -> list[ComponentTyping.VersionFileTypedDict]:
        "Converts the files key in versions.json into a format more suitable for in-line Components."
        return [{
            "version_file_type": version_file_key,
            "accessors": [{
                "accessor_type": accessor_key,
                "arguments": accessor_value
            } for accessor_key, accessor_value in version_file_value.items()]
        } for version_file_key, version_file_value in files.items()]

    def __init__(self, data:ComponentTyping.VersionTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.time = datetime.date.fromisoformat(data["time"]) if data["time"] is not None else None

        self.parent_field = OptionalVersionField.OptionalVersionField(data["parent"], ["parent"])
        self.tags_field = VersionTagListField.VersionTagListField(data["tags"], ["tags"], self)
        self.files_field = VersionFileListField.VersionFileListField(self.normalize_files(data["files"]), ["files"])
        self.fields.extend([self.parent_field, self.tags_field, self.files_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = Version.Version(
            name=self.name,
            time=self.time,
            index=self.get_index(),
        )

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_finals(
            parent=self.parent_field.get_final(),
            tags=list(self.tags_field.map(lambda version_tag_component: version_tag_component.get_final())),
            version_files=list(self.files_field.map(lambda version_file_component: version_file_component.get_final())),
        )

    def check(self) -> list[Exception]:
        exceptions = super().check()
        parent_component = self.parent_field.get_component()
        if parent_component is not None and parent_component is self:
            exceptions.append(Exceptions.InvalidParentVersionError(self.get_final(), parent_component.get_final()))
        if self.time is not None and self.time > datetime.date.today():
            exceptions.append(Exceptions.InvalidVersionTimeError(self.get_final(), self.time, "time is after today"))
        return exceptions

    def finalize(self) -> None:
        super().finalize()
        self.get_final().finalize()
