from typing import Any, Mapping, NotRequired, Required, TypedDict

from Component.Component import Component
from Component.Scripts import Script
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ScriptTypeVerifier,
    SubclassTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionProvider.VersionProvider import (
    VersionProvider,
    VersionProviderCreator,
)


class VersionProviderTypedDict(TypedDict):
    arguments: NotRequired[Mapping[str,Any]]
    version_provider_class: Required[Script[type[VersionProvider]]]

class VersionProviderComponent(Component[VersionProviderCreator, VersionProviderTypedDict]):

    type_name = "VersionProvider"
    object_type = VersionProviderCreator
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, DictTypeVerifier(dict, str, object)),
        TypedDictKeyTypeVerifier("version_provider_class", True, ScriptTypeVerifier(SubclassTypeVerifier(VersionProvider))),
    ))

    def check(self, fields: VersionProviderTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        return fields["version_provider_class"].object.type_verifier.verify(fields.get("arguments", {}), trace)

    def link_final(self, fields: VersionProviderTypedDict) -> None:
        super().link_final(fields)
        self.final.link_version_provider_creator(
            arguments=fields.get("arguments", {}),
            version_provider_class=fields["version_provider_class"].object,
        )
