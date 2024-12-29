import importlib
import importlib.machinery
import importlib.util
from pathlib import Path
from typing import IO, Any, Callable, Iterable, Self

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Utilities.UserInput as UserInput


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

class Script[a]():

    all_type_verifier = TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", additional_function=lambda data: (len(data) == 1, "Can only export a single object"))

    __slots__ = (
        "has_all",
        "module",
        "name",
        "object",
        "path",
    )

    def __init__(self, path: Path, name: str) -> None:
        self.name = name
        self.path = path
        module_name = "_assets.scripts." + name.replace("/", ".").removesuffix(".py")
        self.module = importlib.import_module(module_name)

        self.object:Any = None
        self.has_all:bool = False

    @property
    def should_skip(self) -> bool:
        return not self.has_all

    def finalize(self) -> None:
        self.has_all = hasattr(self.module, "__all__")
        if not self.has_all:
            return
        self.all_type_verifier.base_verify(self.module.__all__, [self])
        exported_object_name = self.module.__all__[0]
        obj = getattr(self.module, exported_object_name, ...)
        if obj is ...:
            raise Exceptions.ScriptFailureError(self, "(name in __all__ does not exist in the module)")
        if hasattr(self.module, "__call_object__"):
            # __call_object__ can be placed in a Python script. If true, it will call the object referenced in `__all__`
            # and use the return value as the object instead of the function itself.
            if self.module.__call_object__ is True:
                obj = obj()
        self.object = obj

    def __call__(self, *args, **kwargs) -> Any:
        return self.object(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def open_file(self) -> IO[str]:
        return open(self.path, "rt")

class Scripts():
    '''Collection of scripts.'''

    def get_script_type(self, suffix:str, name:str) -> type[Script]:
        match suffix:
            case ".py":
                return Script
            case _:
                raise Exceptions.InvalidScriptFileSuffix(suffix, name)

    def should_skip_script(self, suffix:str, relative_name:str, path:Path) -> bool:
        return suffix == ".pyc"

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain
        self.scripts = {relative_name: self.get_script_type(file.suffix, relative_name)(file, relative_name) for file, relative_name in iter_dir(domain.scripts_directory) if not self.should_skip_script(file.suffix, relative_name, file)}
        for script in self.scripts.values():
            script.finalize()
        self.scripts = {script_name: script for script_name, script in self.scripts.items() if not script.should_skip}

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
        return f"<{self.__class__.__name__} {self.scripts}>"

def main(domain:"Domain.Domain") -> None:
    user_script:Script|None = None
    print(domain.scripts)
    user_script = UserInput.input_single(domain.scripts.scripts, "script from the scripts directory", show_options_first_time=True, close_enough=True)
    output = user_script()
    print(output)

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
