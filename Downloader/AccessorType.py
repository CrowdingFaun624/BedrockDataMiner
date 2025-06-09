from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
from Downloader.Accessor import Accessor
from Utilities.Trace import Trace
from Version.VersionFileType import VersionFileType

if TYPE_CHECKING:
    from Version.Version import Version

class AccessorType():

    __slots__ = (
        "accessor_class",
        "class_arguments",
        "full_name",
        "linked_accessor_types",
        "name",
        "propagated_arguments",
    )

    def __init__(self, name:str, full_name:str, class_arguments:dict[str,Any], propagated_arguments:dict[str,Any]) -> None:
        self.name = name
        self.full_name = full_name
        self.class_arguments = class_arguments
        self.propagated_arguments = propagated_arguments
        self.accessor_class:type[Accessor]
        self.linked_accessor_types:dict[str,AccessorType]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def link_finals(
        self,
        accessor_class:type[Accessor],
        get_linked_accessor_types:dict[str,"AccessorType"],
    ) -> None:
        self.accessor_class = accessor_class
        self.linked_accessor_types = get_linked_accessor_types

    def create_accessor(
        self,
        full_name:str,
        trace:Trace,
        version:"Version",
        domain:"Domain.Domain",
        file_type:VersionFileType,
        instance_arguments:dict[str,Any],
        higher_propagated_arguments:dict[str,Any]|None=None,
    ) -> Accessor|None:
        with trace.enter(self, self.name, ...):
            if higher_propagated_arguments is None:
                higher_propagated_arguments = {}
            propagated_arguments = higher_propagated_arguments.copy()
            propagated_arguments.update(self.propagated_arguments)

            linked_accessors:dict[str,Accessor] = {}
            for key, accessor_type in self.linked_accessor_types.items():
                with trace.enter_key(key, accessor_type):
                    subaccessor = accessor_type.create_accessor(full_name + f"({key})", trace, version, domain, file_type, instance_arguments, propagated_arguments)
                    if subaccessor is not None:
                        linked_accessors[key] = subaccessor
                    else:
                        return None

            accessor_type = self.accessor_class
            accessor_instance_keys = accessor_type.instance_parameters.keys_dict.keys()
            accessor_propagated_keys = accessor_type.propagated_parameters.keys_dict.keys()
            local_instance_arguments = {key: value for key, value in instance_arguments.items() if key in accessor_instance_keys}
            local_propagated_arguments = {key: value for key, value in propagated_arguments.items() if key in accessor_propagated_keys}
            if accessor_type.instance_parameters.verify(local_instance_arguments, trace):
                return None
            if accessor_type.propagated_parameters.verify(local_propagated_arguments, trace):
                return None

            return accessor_type(full_name, version, domain, local_instance_arguments, self.class_arguments, propagated_arguments, linked_accessors)
