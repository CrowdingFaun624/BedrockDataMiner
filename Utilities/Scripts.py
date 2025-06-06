import importlib
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable

import Domain.Domain as Domain
from Utilities.Exceptions import ScriptNameCollideError
from Utilities.TypeVerifier import ListTypeVerifier
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

    all_type_verifier = ListTypeVerifier(str, (list, tuple))

    __slots__ = (
        "domain",
        "scripts",
    )

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain
        has_imported_scripts.has_imported_scripts = True

        modules:dict[str,ModuleType] = {}
        for file, relative_name in iter_dir(domain.scripts_directory):
            if file.suffix != ".py": continue
            module_name = f"_domains.{domain.name}.scripts.{relative_name.replace("/", ".").removesuffix(".py")}"
            modules[relative_name] = importlib.import_module(module_name)

        self.scripts:dict[tuple[str,str],Script] = {}
        for relative_name, module in modules.items():
            item_names:list[str]
            if hasattr(module, "__all__"):
                self.all_type_verifier.verify_throw(module.__all__, (relative_name,))
                item_names = module.__all__
            else:
                item_names = dir(module)
            for item_name in item_names:
                self.scripts[relative_name, item_name] = Script(relative_name, item_name, getattr(module, item_name), domain)

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
