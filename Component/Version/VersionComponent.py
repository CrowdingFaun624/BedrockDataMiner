from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

import Utilities.Exceptions as Exceptions
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import VersionFileTypedDict, VersionTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Component.Permissions import InheritancePermissions, InlinePermissions
from Component.Version.VersionFileComponent import (
    VERSION_FILE_PATTERN,
    VersionFileComponent,
)
from Component.VersionTag.VersionTagComponent import VERSION_TAG_PATTERN
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.Version import Version


def compare_to_now(time:datetime) -> bool:
    # this is only for making sure the time isn't significantly ahead of now,
    # so it doesn't need to be that accurate
    if time.tzinfo is None:
        return time > datetime.now()
    else:
        # pretends user is in UTC and adds 1 day.
        return time > datetime.now().replace(tzinfo=timezone.utc)+timedelta(days=1)

VERSION_PATTERN:Pattern["VersionComponent"] = Pattern("is_version")

class VersionComponent(Component[Version]):

    restrict_to_file_names = True
    class_name = "Version"
    my_capabilities = Capabilities(is_version=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("files", True, DictTypeVerifier(dict, str, DictTypeVerifier(dict, str, DictTypeVerifier(dict, str, object)))),
        TypedDictKeyTypeVerifier("parent", True, (str, type(None))),
        TypedDictKeyTypeVerifier("tags", True, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("time", True, (str, type(None))),
        TypedDictKeyTypeVerifier("type", False, str),
    )
    inline_permissions = InlinePermissions.reference
    inheritance_permissions = InheritancePermissions.normal

    @property
    def assume_used(self) -> bool:
        return True

    @classmethod
    def normalize_files(cls, files:dict[str,dict[str,Any]]) -> list[VersionFileTypedDict]:
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

    def initialize_fields(self, data:VersionTypedDict) -> Sequence[Field]:
        self.time = datetime.fromisoformat(data["time"]) if data["time"] is not None else None

        self.parent_field = OptionalComponentField(data["parent"], VERSION_PATTERN, ("parent",))
        self.tags_field = ComponentListField(data["tags"], VERSION_TAG_PATTERN, ("tags",))
        self.files_field = ComponentListField(self.normalize_files(data["files"]), VERSION_FILE_PATTERN, ("files",), assume_type=VersionFileComponent.class_name)
        return (self.parent_field, self.tags_field, self.files_field)

    def create_final(self, trace:Trace) -> Version:
        return Version(
            name=self.name,
            full_name=self.full_name,
            domain=self.domain,
            time=self.time,
            index=self.get_index(),
        )

    def link_finals(self, trace:Trace) -> None:
        self.final.link_finals(
            parent=self.parent_field.map(lambda subcomponent: subcomponent.final),
            tags=list(self.tags_field.map(lambda version_tag_component: version_tag_component.final)),
            version_files=list(self.files_field.map(lambda version_file_component: version_file_component.final)),
        )

    def check(self, trace:Trace) -> None:
        parent_component = self.parent_field.subcomponent
        if parent_component is not None and parent_component is self:
            trace.exception(Exceptions.InvalidParentVersionError(self.final, parent_component.final))
        if self.time is not None and compare_to_now(self.time):
            trace.exception(Exceptions.InvalidVersionTimeError(self.final, self.time, "time is after today"))
