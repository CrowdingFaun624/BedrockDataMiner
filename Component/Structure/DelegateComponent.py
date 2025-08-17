from typing import AbstractSet, Any, Mapping, NotRequired, Required, TypedDict

from Component.Component import Component
from Component.Scripts import Script
from Structure.Delegate.Delegate import Delegate, DelegateCreator
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ScriptTypeVerifier,
    SubclassTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class DelegateTypedDict(TypedDict):
    arguments: NotRequired[Mapping[str, Any]]
    delegate_class: Required[Script[type[Delegate]]]

class DelegateComponent(Component[DelegateCreator, DelegateTypedDict]):

    type_name = "Delegate"
    object_type = DelegateCreator
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, DictTypeVerifier(dict, str, object)),
        TypedDictKeyTypeVerifier("delegate_class", True, ScriptTypeVerifier(SubclassTypeVerifier(Delegate))),
    ))

    def get_propagating_variables(self) -> tuple[dict[str, bool], dict[str, set[object]]]:
        return {"children_has_garbage_collection": False, "cache_versions_for_delegates": False}, {"children_tags": set()}

    def check(self, fields: DelegateTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        type_verifier = fields["delegate_class"].object.type_verifier
        return type_verifier is not None and type_verifier.verify(fields.get("arguments", {}), trace)

    def link_final(self, fields: DelegateTypedDict) -> None:
        super().link_final(fields)
        self.propagating_booleans["cache_versions_for_delegates"] = fields["delegate_class"].object.uses_versions
        self.final.link_delegate_creator(
            arguments=fields.get("arguments", {}),
            delegate_class=fields["delegate_class"].object,
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        return self.final.finalize_delegate_creator(trace)
