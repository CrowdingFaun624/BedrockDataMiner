import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions

BUILT_IN_ACCESSOR_CLASSES:dict[str,type[Accessor.Accessor]] = {accessor_class.__name__: accessor_class for accessor_class in [
    Accessor.Accessor,
    Accessor.DummyAccessor,
    Accessor.SubDirectoryAccessor,
]}

ACCESSOR_CLASSES = ScriptImporter.import_scripted_types("accessors/", BUILT_IN_ACCESSOR_CLASSES, Accessor.Accessor)

class AccessorClassField(Field.Field):

    __slots__ = (
        "accessor_class",
    )

    def __init__(self, accessor_class_str:str, path: list[str | int]) -> None:
        '''
        :accessor_class_str: The name of the Accessor class this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        accessor_class = ACCESSOR_CLASSES.get(accessor_class_str)
        if accessor_class is None:
            raise Exceptions.UnrecognizedAccessorClassError(accessor_class_str)
        self.accessor_class = accessor_class

    def get_final(self) -> type[Accessor.Accessor]:
        return self.accessor_class
