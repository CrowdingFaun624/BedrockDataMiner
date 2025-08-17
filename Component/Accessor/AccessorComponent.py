from typing import Any, Mapping, NotRequired, Required, TypedDict

from Component.Component import Component
from Downloader.AccessorType import AccessorCreator, AccessorType
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class AccessorTypedDict(TypedDict):
    accessor_type: Required[AccessorType]
    arguments: NotRequired[Mapping[Any, Any]]

class AccessorComponent(Component[AccessorCreator, AccessorTypedDict]):

    type_name = "Accessor"
    object_type = AccessorCreator
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessor_type", True, AccessorType),
        TypedDictKeyTypeVerifier("arguments", False, dict)
    ))

    # don't verify arguments. Instance arguments are applied to all linked Accessors, not just the top one referenced by "accessor_type"

    def link_final(self, fields: AccessorTypedDict) -> None:
        super().link_final(fields)
        self.final.link_accessor_creator(
            accessor_type=fields["accessor_type"],
            arguments=fields.get("arguments", {}),
        )
