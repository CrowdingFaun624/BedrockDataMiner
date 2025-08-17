from typing import AbstractSet, Any, Mapping, NotRequired, Sequence

from Component.Structure.StructureComponent import (
    StructureComponent,
    StructureTypedDict,
    tags_type_verifier,
    types_type_verifier,
)
from Structure.Delegate.Delegate import DelegateCreator
from Structure.Function import Function
from Structure.IterableStructure import IterableStructure
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class IterableStructureTypedDict(StructureTypedDict):
    delegate: NotRequired[DelegateCreator | None]
    key_function: NotRequired[Function]
    key_types: NotRequired[type | Sequence[type]]
    required_keys: NotRequired[Sequence[str]]
    tags: NotRequired[StructureTag | Sequence[StructureTag]]
    this_types: NotRequired[type | Sequence[type]]

class IterableStructureComponent[R: IterableStructure, P: IterableStructureTypedDict](StructureComponent[R, P]):

    type_name = "Iterable"
    object_type = IterableStructure
    abstract = True

    default_this_types:tuple[type,...] = ()
    default_key_types:tuple[type,...] = ()
    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate", False, (DelegateCreator, type(None))),
        TypedDictKeyTypeVerifier("key_function", False, Function),
        TypedDictKeyTypeVerifier("key_types", False, types_type_verifier),
        TypedDictKeyTypeVerifier("required_keys", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("tags", False, tags_type_verifier),
        TypedDictKeyTypeVerifier("this_types", False, types_type_verifier),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_iterable_structure(
            delegate=fields.get("delegate", None),
            key_function=fields.get("key_function", lambda data: data),
            key_types=fields.get("key_types", self.default_key_types),
            required_keys=set(fields.get("required_keys", ())),
            tags=fields.get("tags", ()),
            this_types=fields.get("this_types", self.default_this_types),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        return self.final.finalize_iterable_structure(trace)
