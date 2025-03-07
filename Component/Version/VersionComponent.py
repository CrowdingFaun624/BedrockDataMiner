import datetime
from typing import Any

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern
import Component.Version.Field.VersionTagListField as VersionTagListField
import Utilities.Exceptions as Exceptions
import Component.Version.VersionFileComponent as VersionFileComponent
import Utilities.TypeVerifier as TypeVerifier
import Version.Version as Version


def compare_to_now(time:datetime.datetime) -> bool:
    # this is only for making sure the time isn't significantly ahead of now,
    # so it doesn't need to be that accurate
    if time.tzinfo is None:
        return time > datetime.datetime.now()
    else:
        # pretends user is in UTC and adds 1 day.
        return time > datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)+datetime.timedelta(days=1)

VERSION_PATTERN:Pattern.Pattern["VersionComponent"] = Pattern.Pattern("is_version")

class VersionComponent(Component.Component[Version.Version]):

    class_name = "Version"
    my_capabilities = Capabilities.Capabilities(is_version=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("files", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.DictTypeVerifier(dict, str, object, "a dict", "a str", "an object"), "a dict", "a str", "a dict"), "a dict", "a str", "a dict")),
        TypeVerifier.TypedDictKeyTypeVerifier("parent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("time", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    @classmethod
    def normalize_files(cls, files:dict[str,dict[str,Any]]) -> list[ComponentTyping.VersionFileTypedDict]:
        "Converts the files key in versions.json into a format more suitable for inline Components."
        return [{
            "version_file_type": version_file_key,
            "accessors": [{
                "accessor_type": accessor_key,
                "arguments": accessor_value
            } for accessor_key, accessor_value in version_file_value.items()]
        } for version_file_key, version_file_value in files.items()]

    __slots__ = (
        "files_field",
        "parent_field",
        "tags_field",
        "time",
    )

    def initialize_fields(self, data:ComponentTyping.VersionTypedDict) -> list[Field.Field]:
        self.time = datetime.datetime.fromisoformat(data["time"]) if data["time"] is not None else None

        self.parent_field = OptionalComponentField.OptionalComponentField(data["parent"], VERSION_PATTERN, ["parent"], allow_inline=Field.InlinePermissions.reference, assume_component_group="versions")
        self.tags_field = VersionTagListField.VersionTagListField(data["tags"], ["tags"], self)
        self.files_field = ComponentListField.ComponentListField(self.normalize_files(data["files"]), VersionFileComponent.VERSION_FILE_PATTERN, ["files"], allow_inline=Field.InlinePermissions.inline, assume_type=VersionFileComponent.VersionFileComponent.class_name)
        return [self.parent_field, self.tags_field, self.files_field]

    def create_final(self) -> Version.Version:
        return Version.Version(
            name=self.name,
            domain=self.domain,
            time=self.time,
            index=self.get_index(),
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_finals(
            parent=self.parent_field.get_final(lambda subcomponent: subcomponent.final),
            tags=list(self.tags_field.map(lambda version_tag_component: version_tag_component.final)),
            version_files=list(self.files_field.map(lambda version_file_component: version_file_component.final)),
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        parent_component = self.parent_field.subcomponent
        if parent_component is not None and parent_component is self:
            exceptions.append(Exceptions.InvalidParentVersionError(self.final, parent_component.final))
        if self.time is not None and compare_to_now(self.time):
            exceptions.append(Exceptions.InvalidVersionTimeError(self.final, self.time, "time is after today"))
        return exceptions
