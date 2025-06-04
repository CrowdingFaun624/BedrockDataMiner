from typing import Sequence

import Utilities.Exceptions as Exceptions
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import TypeAliasTypedDict
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

TYPE_ALIAS_PATTERN:Pattern["TypeAliasComponent"] = Pattern("is_type_alias")

class TypeAliasComponent(Component[tuple[type,...]]):

    class_name = "TypeAlias"
    my_capabilities = Capabilities(is_type_alias=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("type", False, str),
        TypedDictKeyTypeVerifier("types", True, ListTypeVerifier(str, list)),
    )

    __slots__ = (
        "types_strs",
    )

    def initialize_fields(self, data: TypeAliasTypedDict) -> Sequence[Field]:
        self.types_strs = data["types"]
        return ()

    def create_final(self, trace:Trace) -> tuple[type,...]:
        final:list[type] = []
        already_types:set[str] = set()
        default_types = self.domain.type_stuff.default_types
        for type_str in self.types_strs:
            with trace.enter(self, self.name, type_str):
                if type_str in already_types:
                    trace.exception(Exceptions.ComponentDuplicateTypeError(type_str))
                already_types.add(type_str)
                if type_str in default_types:
                    final.append(default_types[type_str])
                else:
                    trace.exception(Exceptions.ComponentUnrecognizedTypeError(type_str))
        return tuple(final)
