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
        "arguments",
        "full_name",
        "linked_accessor_types",
        "name",
    )

    def __init__(self, name:str, full_name:str, arguments:dict[str,Any]) -> None:
        self.name = name
        self.full_name = full_name
        self.arguments = arguments
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
    ) -> Accessor|None:
        with trace.enter(self, self.name, ...):
            linked_accessors:dict[str,Accessor] = {}
            for key, accessor_type in self.linked_accessor_types.items():
                with trace.enter_key(key, accessor_type):
                    subaccessor = accessor_type.create_accessor(full_name + f"({key})", trace, version, domain, file_type, instance_arguments)
                    if subaccessor is not None:
                        linked_accessors[key] = subaccessor
                    else:
                        return None

            accessor_type = self.accessor_class
            accessor_instance_keys = accessor_type.instance_parameters.keys_dict.keys()
            local_instance_arguments = {key: value for key, value in instance_arguments.items() if key in accessor_instance_keys}
            if accessor_type.instance_parameters.verify(local_instance_arguments, trace):
                return None

            return accessor_type(full_name, version, domain, local_instance_arguments, self.arguments, linked_accessors)
