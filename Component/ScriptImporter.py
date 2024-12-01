from typing import Generic, Optional, TypeVar

import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts

a = TypeVar("a")

class ScriptSet(Generic[a]):

    def __init__(self, all_scripts:dict[str,Scripts.Script], scripts_by_name:dict[str,Scripts.Script], scripts_by_file:dict[str,Scripts.Script], built_in_objects:dict[str,a]) -> None:
        self.all_scripts = all_scripts
        self.scripts_by_name = scripts_by_name
        self.scripts_by_file = scripts_by_file
        self.built_in_objects = built_in_objects

    def __contains__(self, key:str) -> bool:
        return key in self.built_in_objects or key in self.scripts_by_name or key in self.scripts_by_file

    def __getitem__(self, key:str) -> a:
        return self.get(key)

    def get(self, key:str, message:Optional[str]=None) -> a:
        if key in self.built_in_objects:
            return self.built_in_objects[key]
        script = self.scripts_by_name.get(key)
        if script is None:
            script = self.scripts_by_file.get(key)
        if script is None:
            print(self.scripts_by_file)
            script = self.all_scripts.get(key)
            if script is None:
                raise Exceptions.UnrecognizedScriptError(key, message=message)
            else:
                raise Exceptions.WrongScriptError(script, message=message)
        return script.object

def import_scripted_types(folder:str, built_in_classes:dict[str,type[a]], required_superclass:type[a]) -> ScriptSet[type[a]]:
    '''
    :folder: The subfolder of scripts that contains the desired type.
    :built_in_classes: Classes that Lua Scripts can inherit from.
    :required_superclass: Type that Python scripts must export.
    '''
    scripts = Scripts.scripts.scripts
    scripts_by_file:dict[str,Scripts.Script[type[a]]] = {}
    scripts_by_name:dict[str,Scripts.Script[type[a]]] = {}
    double_use_scripts:set[str] = set()
    for file_name, script in scripts.items():
        object_class = script.object
        if not isinstance(object_class, type):
            if file_name.startswith(folder):
                raise Exceptions.InvalidScriptObjectTypeError(script, script.object, [required_superclass])
            else:
                continue
        if not issubclass(object_class, required_superclass):
            if file_name.startswith(folder):
                raise Exceptions.ScriptedClassMissingInheritError(object_class.__name__)
            else:
                continue
        scripts_by_file[file_name] = script
        if object_class.__name__ not in double_use_scripts:
            if object_class.__name__ in scripts_by_name:
                double_use_scripts.add(object_class.__name__)
                del scripts_by_name[object_class.__name__]
            else:
                scripts_by_name[object_class.__name__] = script
    return ScriptSet(Scripts.scripts.scripts, scripts_by_name, scripts_by_file, built_in_classes)
