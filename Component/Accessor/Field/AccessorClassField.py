import Component.Field.Field as Field
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts

BUILT_IN_ACCESSOR_CLASSES:dict[str,type[Accessor.Accessor]] = {accessor_class.__name__: accessor_class for accessor_class in [
    Accessor.Accessor,
    Accessor.DummyAccessor,
    Accessor.SubDirectoryAccessor
]}

def import_accessor_classes() -> dict[str,type[Accessor.Accessor]]:
    accessor_scripts = Scripts.scripts.get_all_in_directory("accessors/")
    accessor_classes:dict[str,type[Accessor.Accessor]] = {}
    accessor_classes.update(BUILT_IN_ACCESSOR_CLASSES)
    for file_name, script in accessor_scripts.items():
        if isinstance(script, Scripts.LuaScript):
            class_name = file_name.removeprefix("accessors/").removesuffix(".lua").replace("/", ".")
            attributes = dict(script.content)
            inherit_from:str|None = attributes.pop("inherit", None)
            if inherit_from is None:
                raise Exceptions.AccessorClassMissingInheritError(class_name)
            superclass = BUILT_IN_ACCESSOR_CLASSES.get(inherit_from)
            if superclass is None:
                raise Exceptions.AccessorClassInheritUnrecognizedAccessorClassError(class_name, inherit_from)
            accessor_classes[class_name] = type(class_name, (superclass, Scripts.ScriptedObject), attributes)
        else:
            raise NotImplementedError
    return accessor_classes

ACCESSOR_CLASSES = import_accessor_classes()

class AccessorClassField(Field.Field):

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
