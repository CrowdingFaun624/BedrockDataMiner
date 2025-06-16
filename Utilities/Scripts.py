import importlib
from pathlib import Path
from typing import Any, Callable, Iterable

import Domain.Domain as Domain
from Utilities.Exceptions import ScriptNameCollideError
from Utilities.UserInput import input_single


class HasImportedScripts():

    __slots__ = (
        "has_imported_scripts",
    )

    def __init__(self) -> None:
        self.has_imported_scripts:bool = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.has_imported_scripts}>"

has_imported_scripts = HasImportedScripts()

def iter_dir(path:Path, prepension:str="") -> Iterable[tuple[Path,str]]:
    if not path.exists():
        return
    already_stems:dict[str,Path] = {}
    for subpath in path.iterdir():
        if subpath.is_file():
            if subpath.stem in already_stems:
                raise ScriptNameCollideError(already_stems[subpath.stem], subpath)
            already_stems[subpath.stem] = subpath
            yield (subpath, prepension + subpath.stem)
        else:
            yield from iter_dir(subpath, prepension + subpath.name + "/")

class Script[a]():

    __slots__ = (
        "domain",
        "file_name",
        "object",
        "object_name",
    )

    def __init__(self, file_name: str, object_name:str, object:a, domain:"Domain.Domain") -> None:
        self.file_name:str = file_name
        self.object_name:str = object_name
        self.object:a = object
        self.domain:"Domain.Domain" = domain

    def __call__(self:"Script[Callable]", *args, **kwargs) -> Any:
        return self.object(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name}!{self.file_name} {self.object_name}>"

class Scripts():
    '''Collection of scripts.'''

    __slots__ = (
        "domain",
        "scripts",
    )

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain
        has_imported_scripts.has_imported_scripts = True
        self.scripts:dict[tuple[str,str],Script] = {}

    def import_modules(self) -> None:
        for file, relative_name in iter_dir(self.domain.scripts_directory):
            if file.suffix != ".py": continue
            module_name = f"_domains.{self.domain.name}.scripts.{relative_name.replace("/", ".").removesuffix(".py")}"
            importlib.import_module(module_name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name} {self.scripts}>"

def main(domain:"Domain.Domain") -> None:
    user_script:Script|None = None
    script_files = {item: item for item in sorted(set(file_name for file_name, object_name in domain.scripts.scripts))}
    user_file = input_single(script_files, "file from the scripts directory", show_options_first_time=True, close_enough=True)
    file_objects = {object_name: script for (file_name, object_name), script in domain.scripts.scripts.items() if file_name == user_file}
    user_script = input_single(file_objects, f"object from \"{user_file}\"", show_options_first_time=True, close_enough=True)
    output = user_script()
    print(output)
