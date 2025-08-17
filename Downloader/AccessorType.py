from typing import TYPE_CHECKING, Any, Mapping

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Downloader.Accessor import Accessor
from Utilities.Trace import Trace
from Version.VersionFileType import VersionFileType

if TYPE_CHECKING:
    from Version.Version import Version

class AccessorType(ComponentObject):

    __slots__ = (
        "accessor_class",
        "arguments",
        "linked_accessor_types",
    )

    def link_accessor_type(
        self,
        accessor_class:type[Accessor],
        arguments:Mapping[Any,Any],
        linked_accessor_types:Mapping[str,"AccessorType"],
    ) -> None:
        self.accessor_class = accessor_class
        self.arguments = arguments
        self.linked_accessor_types = linked_accessor_types

    def create_accessor(
        self,
        full_name:str,
        trace:Trace,
        version:"Version",
        domain:"Domain.Domain",
        file_type:VersionFileType,
        instance_arguments:Mapping[Any,Any],
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

class AccessorCreator(ComponentObject):
    """
    Object that creates Accessors. This is necessary because Accessors must know what their Version is.
    """

    __slots__ = (
        "accessor_type",
        "instance_arguments",
    )

    def link_accessor_creator(self, accessor_type:AccessorType, arguments:Mapping[Any, Any]={}) -> None:
        self.accessor_type = accessor_type
        self.instance_arguments = arguments

    def create_accessor(self, version:"Version", domain:"Domain.Domain", file_type:VersionFileType, trace:Trace) -> Accessor|None:
        return self.accessor_type.create_accessor(self.full_name, trace, version, domain, file_type, self.instance_arguments)
