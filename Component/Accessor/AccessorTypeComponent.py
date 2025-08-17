from typing import Any, Mapping, NotRequired, Required, TypedDict

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.Scripts import Script
from Downloader.Accessor import Accessor
from Downloader.AccessorType import AccessorType
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ScriptTypeVerifier,
    SubclassTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class AccessorTypeTypedDict(TypedDict):
    accessor_class: Required[Script[type[Accessor]]]
    arguments: NotRequired[Mapping[Any, Any]]
    linked_accessors: NotRequired[Mapping[str, AccessorType]]

class AccessorTypeComponent(Component[AccessorType, AccessorTypeTypedDict]):

    type_name = "AccessorType"
    object_type = AccessorType
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessor_class", True, ScriptTypeVerifier(SubclassTypeVerifier(Accessor))),
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("linked_accessors", False, DictTypeVerifier(dict, str, AccessorType))
    ))

    def link_final(self, fields: AccessorTypeTypedDict) -> None:
        super().link_final(fields)
        self.final.link_accessor_type(
            accessor_class=fields["accessor_class"].object,
            arguments=fields.get("arguments", {}),
            linked_accessor_types=fields.get("linked_accessors", {}),
        )

    def post_check(self, fields: AccessorTypeTypedDict, trace: Trace) -> bool:
        if super().post_check(fields, trace):
            return True
        linked_accessors = fields.get("linked_accessors", {})
        linked_accessor_types = fields["accessor_class"].object.linked_accessor_types
        has_error:bool = False
        for key, accessor_class in linked_accessor_types.items():
            with trace.enter_key(key, accessor_class):
                if key not in linked_accessors:
                    trace.exception(Exceptions.LinkedComponentMissingError(key, accessor_class))
                    has_error = True
        for key, accessor in linked_accessors.items():
            with trace.enter_key(key, accessor):
                if key not in linked_accessor_types:
                    trace.exception(Exceptions.LinkedComponentExtraError(key, accessor, [key for key in linked_accessors if key not in linked_accessor_types]))
                    has_error = True
                required_type = linked_accessor_types.get(key)
                if required_type is not None and not issubclass(accessor.accessor_class, required_type):
                    trace.exception(Exceptions.LinkedComponentTypeError(key, required_type, accessor.accessor_class))
                    has_error = True
        return has_error
