from typing import TypeVar

import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts

a = TypeVar("a")

def import_scripted_types(folder:str, built_in_classes:dict[str,type[a]], required_superclass:type[a]) -> dict[str,type[a]]:
    '''
    :folder: The subfolder of scripts that contains the desired type.
    :built_in_classes: Classes that Lua Scripts can inherit from.
    :required_superclass: Type that Python scripts must export.
    '''
    scripts = Scripts.scripts.get_all_in_directory(folder)
    classes:dict[str,type[a]] = {}
    classes.update(built_in_classes)
    for file_name, script in scripts.items():
        match script:
            case Scripts.LuaScript():
                class_name = file_name.removeprefix(folder).removesuffix(".lua").replace("/", ".")
                attributes = dict(script.content)
                inherit_from:str|None = attributes.pop("inherit", None)
                if inherit_from is None:
                    raise Exceptions.ScriptedClassMissingInheritError(class_name)
                superclass = built_in_classes.get(inherit_from)
                if superclass is None:
                    raise Exceptions.ScriptedClassInheritUnrecognizedClassError(class_name, inherit_from)
                classes[class_name] = type(class_name, (superclass, Scripts.ScriptedObject), attributes) # type: ignore
            case Scripts.PythonScript():
                object_class = script.object
                if not isinstance(object_class, type):
                    raise Exceptions.InvalidScriptObjectTypeError(script.object, [required_superclass])
                if not issubclass(object_class, required_superclass):
                    raise Exceptions.ScriptedClassMissingInheritError(object_class.__name__)
                classes[object_class.__name__] = object_class
            case _:
                raise Exceptions.InvalidScriptTypeError(type(script), [Scripts.LuaScript, Scripts.PythonScript])
    return classes
