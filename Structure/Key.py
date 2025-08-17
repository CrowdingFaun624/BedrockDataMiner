from typing import Any, Mapping

from Component.ComponentObject import ComponentObject
from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Filter import Filter
from Structure.Structure import (
    Structure,
    convert_tags_to_set,
    convert_types_to_tuple,
    tags_type,
    types_type,
)


class Key[V](ComponentObject):

    __slots__ = (
        "delegate_arguments",
        "filter",
        "finalized",
        "required",
        "similarity_weight",
        "structure",
        "tag_list",
        "tags",
        "type_list",
        "types",
        "value_weight",
    )

    def link_key(
        self,
        delegate_arguments:Mapping[str,Any]|None,
        filter:Filter|None,
        required:bool,
        similarity_weight:int,
        structure:Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], Any, Any]|None,
        tags:tags_type,
        types:types_type,
        value_weight:int|None,
    ) -> None:
        self.structure = structure
        self.tag_list = tags
        self.type_list = types
        # since Keys can be placed anywhere that their subclasses can, these attributes
        # hold default values for the exclusive attributes of Key's subclasses.
        self.delegate_arguments = delegate_arguments
        self.filter = filter
        self.required = required
        self.similarity_weight = similarity_weight
        self.value_weight = value_weight
        self.finalized = False

    # Structures and Components are expected to call this method,
    # since the finalize method of many Structures requires `finalize` to
    # be called on Keys, but that may not be so.
    def finalize_key(self) -> None:
        if self.finalized: return
        self.finalized = True
        self.tags = convert_tags_to_set(self.tag_list)
        del self.tag_list
        self.types = convert_types_to_tuple(self.type_list)
        del self.type_list
