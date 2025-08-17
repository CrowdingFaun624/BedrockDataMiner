from typing import Any, Callable, Mapping, NotRequired, Required, TypedDict

from Component.Component import Component
from Component.Scripts import Script
from Structure.Function import Function
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ScriptTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class FunctionTypedDict(TypedDict):
    arguments: NotRequired[Mapping[str, Any]]
    function: Required[Script[Callable[..., Any]]]

class FunctionComponent(Component[Function, FunctionTypedDict]):

    type_name = "Function"
    object_type = Function
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, DictTypeVerifier(dict, str, object)),
        TypedDictKeyTypeVerifier("function", True, ScriptTypeVerifier(object, lambda data: (callable(data), "must be callable"))),
    ))

    def check(self, fields: FunctionTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        if fields["function"].type_verifier is not None:
            return fields["function"].type_verifier.verify(fields.get("arguments", {}), trace)
        return False

    def get_propagating_variables(self) -> tuple[dict[str, bool], dict[str, set[object]]]:
        return {"children_has_garbage_collection": False, "cache_versions_for_delegates": False}, {"children_tags": set()}

    def link_final(self, fields: FunctionTypedDict) -> None:
        super().link_final(fields)
        self.final.link_function(
            arguments=fields.get("arguments", {}),
            function=fields["function"],
        )
