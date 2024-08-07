import importlib
import importlib.machinery
import importlib.util
import sys
from itertools import accumulate
from typing import IO, Any, Callable, Iterable

import jqpy  # library that doesn't let me compile but will work on Windows
import lupa  # looks like this has no type hinting whatsoever
from pathlib2 import Path
from typing_extensions import Self

import Utilities.DataFile as DataFile
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

EmptyInput = jqpy.EmptyInput

def iter_dir(path:Path, prepension:str="") -> Iterable[tuple[Path,str]]:
    already_stems:dict[str,Path] = {}
    for subpath in path.iterdir():
        if subpath.is_file():
            if subpath.stem in already_stems:
                raise Exceptions.ScriptNameCollideError(already_stems[subpath.stem], subpath)
            already_stems[subpath.stem] = subpath
            yield (subpath, prepension + subpath.stem)
        else:
            yield from iter_dir(subpath, prepension + subpath.name + "/")

class _ScriptDependencies():
    '''Class for holding stuff necessary for Scripts to run, like the LuaRuntime'''

    def __init__(self, lua_runtime:lupa.LuaRuntime) -> None:
        self.lua_runtime = lua_runtime

class AbstractScript():

    def __repr__(self) -> str:
        return "<%s>" % (self.__class__.__name__)

class Script(AbstractScript):
    '''Abstract class for scripts.'''

    def __init__(self, path:Path, name:str, script_dependencies:_ScriptDependencies) -> None:
        self.name = name
        self.path = path

    def finalize(self) -> None:
        '''
        Runs after all scripts have been initialized.
        '''

    def open_file(self) -> IO[str]:
        return open(self.path, "rt")

    def __call__(self, data:Any|None=None) -> Any: ...

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

class JQScript(Script):

    def __init__(self, path: Path, name: str, script_dependencies:_ScriptDependencies) -> None:
        super().__init__(path, name, script_dependencies)
        with self.open_file() as f:
            self.program = f.read()

    def __call__(self, data:jqpy.JSON|jqpy._TEmptyInput=EmptyInput) -> Any:
        return jqpy.jq(self.program, data)

class LuaScript(Script):

    def __init__(self, path: Path, name: str, script_dependencies:_ScriptDependencies) -> None:
        super().__init__(path, name, script_dependencies)
        with self.open_file() as f:
            self.compiled_program = script_dependencies.lua_runtime.compile(f.read())
            self.content = self.compiled_program() # get stored content

    def __call__(self, data:list[Any]|None=None) -> Any:
        if data is None: data = []
        return self.content(data)

class EvilModule():
    '''
    Use `setattr` to set attributes of this object to other EvilModules or actual modules.
    Used to mimic a directory in the scripts folder.
    '''
    pass

class PythonScript(Script):

    all_type_verifier = TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", additional_function=lambda data: (len(data) == 1, "Can only export a single object"))

    def __init__(self, path: Path, name: str, script_dependencies: _ScriptDependencies) -> None:
        super().__init__(path, name, script_dependencies)
        module_name = "scripts.%s" % (name.replace("/", ".").removesuffix(".py"),)
        stem = name.split("/")[-1].removesuffix(".py")

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            raise Exceptions.ScriptFailureError(self, "(spec is None)")
        self.spec = spec
        self.module = importlib.util.module_from_spec(self.spec)
        sys.modules[module_name] = self.module

        module_parents = list(accumulate(name.split("/")[:-1], func=lambda a, b: "%s.%s" % (a, b), initial="scripts"))
        module_parents.reverse()
        # for example: name = scripts/normalizers/bar/foo.py, module_parents = ["scripts.normalizers.bar", "scripts.normalizers""scripts"]
        previous_module = self.module
        previous_module_name = stem
        for parent in module_parents:
            if parent in sys.modules:
                evil_module = sys.modules[parent]
            else:
                evil_module = EvilModule()
                sys.modules[parent] = evil_module # type: ignore
            evil_module = sys.modules.get(parent, EvilModule())
            if not hasattr(evil_module, previous_module_name):
                setattr(evil_module, previous_module_name, previous_module)
            previous_module = evil_module
            previous_module_name = parent.split(".")[-1]

        self.object:Any = None

    @property
    def should_finalize(self) -> bool:
        return not self.path.name.startswith("__") and not any(parent.name.startswith("__") for parent in self.path.relative_to(FileManager.SCRIPTS_DIRECTORY).parents)

    def finalize(self) -> None:
        if self.spec.loader is None:
            raise Exceptions.ScriptFailureError(self, "(spec loader is None)")
        self.spec.loader.exec_module(self.module)
        if self.should_finalize:
            if not hasattr(self.module, "__all__"):
                raise Exceptions.ScriptFailureError(self, "(__all__ does not exist in the module)")
            self.all_type_verifier.base_verify(self.module.__all__, [self])
            exported_object_name = self.module.__all__[0]
            obj = getattr(self.module, exported_object_name, ...)
            if obj is ...:
                raise Exceptions.ScriptFailureError(self, "(name in __all__ does not exist in the module)")
            self.object = obj

    def __call__(self, *args, **kwargs) -> Any:
        return self.object(*args, **kwargs)

class InlineScript(AbstractScript):

    def __init__(self, program:str, script_dependencies:_ScriptDependencies) -> None:
        self.program = program

class JQInlineScript(InlineScript):

    def __init__(self, program:str, script_dependencies: _ScriptDependencies) -> None:
        super().__init__(program, script_dependencies)

class Scripts():
    '''Collection of scripts.'''

    def get_script_type(self, suffix:str, name:str) -> type[Script]:
        match suffix:
            case ".jq":
                return JQScript
            case ".lua":
                return LuaScript
            case ".py":
                return PythonScript
            case _:
                raise Exceptions.InvalidScriptFileSuffix(suffix, name)

    def should_skip_script(self, suffix:str, relative_name:str, path:Path) -> bool:
        return suffix == ".pyc"

    def __init__(self) -> None:
        self.lua_runtime = lupa.LuaRuntime()
        self.lua_runtime.globals()["bdd"] = {
            "data_files": DataFile.data_files,
        }
        script_dependencies = _ScriptDependencies(self.lua_runtime)
        self.scripts = {relative_name: self.get_script_type(file.suffix, relative_name)(file, relative_name, script_dependencies) for file, relative_name in iter_dir(FileManager.SCRIPTS_DIRECTORY) if not self.should_skip_script(file.suffix, relative_name, file)}
        for script in self.scripts.values():
            script.finalize()

    def __getitem__(self, name:str) -> Script:
        output = self.scripts.get(name, None)
        if output is None:
            raise Exceptions.UnrecognizedScriptError(name)
        return output

    def get_all_in_directory(self, directory_name:str) -> dict[str,Script]:
        '''
        Returns all scripts whose full names start with `directory_name`.
        :directory_name: The directory name, ending in "/", to select from.
        '''
        return {script_name: script for script_name, script in self.scripts.items() if script_name.startswith(directory_name)}

    def __repr__(self) -> str:
        return "<Scripts %s>" % (self.scripts)

def main() -> None:
    user_script:Script|None = None
    print(scripts)
    while user_script is None:
        user_script = scripts.scripts.get(input("Choose a script from the scripts directory: "), None)
    output = user_script()
    print(output)

scripts = Scripts()

class ScriptedObject():
    '''
    Subclasses of ScriptedObject will have all unbound functions be bound to them.
    '''

    def __new__(cls, *args, **kwargs) -> Self:
        def make_the_function(self: Self, func:Callable) -> Callable:
            return lambda *function_arguments, **function_keyword_arguments: func(self, *function_arguments, **function_keyword_arguments)
        output = super().__new__(cls)
        for attribute in cls.__dict__:
            attr = getattr(output, attribute)
            if not attribute.startswith("__") and callable(attr) and not isinstance(attr, type):
                setattr(output, attribute, make_the_function(output, attr))
        return output
