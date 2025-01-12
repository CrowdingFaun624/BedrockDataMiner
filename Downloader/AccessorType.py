from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
import Downloader.Accessor as Accessor
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFileType as VersionFileType

if TYPE_CHECKING:
    import Version.Version as Version

class AccessorType():

    __slots__ = (
        "accessor_class",
        "class_arguments",
        "linked_accessor_types",
        "name",
        "propagated_arguments",
    )

    def __init__(self, name:str, class_arguments:dict[str,Any], propagated_arguments:dict[str,Any]) -> None:
        self.name = name
        self.class_arguments = class_arguments
        self.propagated_arguments = propagated_arguments
        self.accessor_class:type[Accessor.Accessor]
        self.linked_accessor_types:dict[str,AccessorType]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def link_finals(
        self,
        accessor_class:type[Accessor.Accessor],
        get_linked_accessor_types:dict[str,"AccessorType"],
    ) -> None:
        self.accessor_class = accessor_class
        self.linked_accessor_types = get_linked_accessor_types

    def create_accessor(
        self,
        version:"Version.Version",
        domain:"Domain.Domain",
        file_type:VersionFileType.VersionFileType,
        instance_arguments:dict[str,Any],
        higher_propagated_arguments:dict[str,Any]|None=None,
    ) -> tuple[Accessor.Accessor|None,list[Exception]]:
        if higher_propagated_arguments is None:
            higher_propagated_arguments = {}
        propagated_arguments = higher_propagated_arguments.copy()
        propagated_arguments.update(self.propagated_arguments)

        linked_accessors:dict[str,Accessor.Accessor] = {}
        exceptions:list[Exception] = []
        for key, accessor_type in self.linked_accessor_types.items():
            subaccessor, new_exceptions = accessor_type.create_accessor(version, domain, file_type, instance_arguments, propagated_arguments)
            if subaccessor is not None:
                linked_accessors[key] = subaccessor
            exceptions.extend(new_exceptions)

        accessor_type = self.accessor_class
        accessor_instance_keys = accessor_type.instance_parameters.keys_dict.keys()
        accessor_propagated_keys = accessor_type.propagated_parameters.keys_dict.keys()
        local_instance_arguments = {key: value for key, value in instance_arguments.items() if key in accessor_instance_keys}
        local_propagated_arguments = {key: value for key, value in propagated_arguments.items() if key in accessor_propagated_keys}
        trace = TypeVerifier.StackTrace([(self, TypeVerifier.TraceItemType.OTHER), (version, TypeVerifier.TraceItemType.OTHER)])
        exceptions.extend(accessor_type.instance_parameters.verify(local_instance_arguments, trace))
        exceptions.extend(accessor_type.propagated_parameters.verify(local_propagated_arguments, trace))

        if len(exceptions) > 0:
            return None, exceptions
        else:
            return accessor_type(self.name, version, domain, local_instance_arguments, self.class_arguments, propagated_arguments, linked_accessors), exceptions
