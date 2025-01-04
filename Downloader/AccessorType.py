from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFileType as VersionFileType

if TYPE_CHECKING:
    import Version.Version as Version

class AccessorType():

    def __init__(self, name:str, class_arguments:dict[str,Any]) -> None:
        self.name = name
        self.class_arguments = class_arguments
        self.accessor_class:type[Accessor.Accessor]|None = None
        self.linked_accessor_types:dict[str,AccessorType]|None = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def link_finals(
        self,
        accessor_class:type[Accessor.Accessor],
        get_linked_accessor_types:dict[str,"AccessorType"],
    ) -> None:
        self.accessor_class = accessor_class
        self.linked_accessor_types = get_linked_accessor_types

    def get_accessor_class(self) -> type[Accessor.Accessor]:
        if self.accessor_class is None:
            raise Exceptions.AttributeNoneError("accessor_class", self)
        return self.accessor_class

    def get_linked_accessor_types(self) -> dict[str,"AccessorType"]:
        if self.linked_accessor_types is None:
            raise Exceptions.AttributeNoneError("linked_accessor_types", self)
        return self.linked_accessor_types

    def create_accessor(self, version:"Version.Version", domain:"Domain.Domain", file_type:VersionFileType.VersionFileType, instance_arguments:dict[str,Any]) -> tuple[Accessor.Accessor|None,list[Exception]]:
        linked_accessors:dict[str,Accessor.Accessor] = {}
        exceptions:list[Exception] = []
        for key, accessor_type in self.get_linked_accessor_types().items():
            subaccessor, new_exceptions = accessor_type.create_accessor(version, domain, file_type, instance_arguments)
            if subaccessor is not None:
                linked_accessors[key] = subaccessor
            exceptions.extend(new_exceptions)
        accessor_type = self.get_accessor_class()
        accessor_instance_keys = accessor_type.instance_parameters.keys_dict.keys()
        local_instance_arguments = {key: value for key, value in instance_arguments.items() if key in accessor_instance_keys}
        trace = TypeVerifier.Trace([(self, TypeVerifier.TraceItemType.OTHER), (version, TypeVerifier.TraceItemType.OTHER)])
        exceptions.extend(accessor_type.instance_parameters.verify(local_instance_arguments, trace))
        if len(exceptions) > 0:
            return None, exceptions
        else:
            return accessor_type(version, domain, local_instance_arguments, self.class_arguments, linked_accessors), exceptions
