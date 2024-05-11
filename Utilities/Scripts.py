from typing import Any, IO, Iterable

import jqpy # library that doesn't let me compile but will work on Windows
import lupa # looks like this has no type hinting whatsoever
from pathlib2 import Path

import Utilities.FileManager as FileManager

EmptyInput = jqpy.EmptyInput

def iter_dir(path:Path, prepension:str="") -> Iterable[tuple[Path,str]]:
    for subpath in path.iterdir():
        if subpath.is_file():
            yield (subpath, prepension + subpath.name)
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

    def __call__(self, data:list[Any]|None=None) -> Any:
        if data is None: data = []
        return self.compiled_program(data)

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
            case _:
                raise ValueError("Invalid file suffix \"%s\" on file \"%s\"" % (suffix, name))

    def __init__(self) -> None:
        self.lua_runtime = lupa.LuaRuntime()
        script_dependencies = _ScriptDependencies(self.lua_runtime)
        self.scripts = {relative_name: self.get_script_type(file.suffix, relative_name)(file, relative_name, script_dependencies) for file, relative_name in iter_dir(FileManager.SCRIPTS_FOLDER)}

    def __getitem__(self, name:str) -> Script:
        output = self.scripts.get(name, None)
        if output is None:
            raise FileNotFoundError("Script \"%s\" does not exist!" % (name,))
        return output

    def __repr__(self) -> str:
        return "<Scripts %s>" % (self.scripts)

def main() -> None:
    user_script:Script|None = None
    print(scripts)
    while user_script is None:
        user_script = scripts.scripts.get(input("Choose a script from the scripts directory: "), None)
    output = user_script()
    print(output(5))
    # print(dir(output))
    # print(output.__class__)
    # print([func() for func in output.values()])



scripts = Scripts()
