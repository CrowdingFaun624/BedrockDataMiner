from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import TypeAliasTypedDict
from Component.Field.Field import Field
from Component.Permissions import InlinePermissions
from Component.Structure.Field.TypeListField import TypeListField
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class TypeAliasComponent(Component[TypeListField]): # truly unusual Component type

    class_name = "TypeAlias"
    my_capabilities = Capabilities(is_type_alias=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("type", False, str),
        TypedDictKeyTypeVerifier("types", True, ListTypeVerifier(str, list)),
    )
    inline_permissions = InlinePermissions.reference

    __slots__ = (
        "types_field",
    )

    def initialize_fields(self, data: TypeAliasTypedDict) -> Sequence[Field]:
        self.types_field = TypeListField(data["types"], ("types",))
        return (self.types_field,)

    def create_final(self, trace:Trace) -> TypeListField:
        return self.types_field
