import Component.Field.Field as Field
import Domain.Domain as Domain
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions


class AccessorClassField(Field.Field):

    __slots__ = (
        "accessor_class",
    )

    def __init__(self, accessor_class_str:str, domain:"Domain.Domain", path: list[str | int]) -> None:
        '''
        :accessor_class_str: The name of the Accessor class this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        accessor_class = domain.accessor_classes.get(accessor_class_str)
        if accessor_class is None:
            raise Exceptions.UnrecognizedAccessorClassError(accessor_class_str)
        self.accessor_class = accessor_class

    def get_final(self) -> type[Accessor.Accessor]:
        return self.accessor_class
