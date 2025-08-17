from typing import AbstractSet, Any, Mapping, NotRequired, Required, TypedDict

from Component.Component import Component
from Component.Scripts import Script
from Serializer.Serializer import Serializer, SerializerCreator
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ScriptTypeVerifier,
    SubclassTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class SerializerTypedDict(TypedDict):
    arguments: NotRequired[Mapping[Any, Any]]
    serializer_class: Required[Script[type[Serializer]]]

class SerializerComponent(Component[SerializerCreator, SerializerTypedDict]):

    type_name = "Serializer"
    object_type = SerializerCreator
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("serializer_class", True, ScriptTypeVerifier(SubclassTypeVerifier(Serializer))),
    ))

    def get_propagating_variables(self) -> tuple[dict[str, bool], dict[str, set[object]]]:
        return {"children_has_garbage_collection": True}, {}

    def check(self, fields: SerializerTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        type_verifier = fields["serializer_class"].object.type_verifier
        return type_verifier is not None and type_verifier.verify(fields.get("arguments", {}), trace)

    def link_final(self, fields: SerializerTypedDict) -> None:
        super().link_final(fields)
        self.final.link_serializer_creator(
            fields.get("arguments", {}),
            serializer_class=fields["serializer_class"].object,
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_serializer_creator()
        return False
