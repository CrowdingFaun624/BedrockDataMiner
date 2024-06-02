from typing import TYPE_CHECKING, Any, Callable, Literal, overload

from pathlib2 import Path
from typing_extensions import Self

import Downloader.Manager as Manager
import Utilities.FileManager as FileManager

if TYPE_CHECKING:
    import Version.Version as Version

class Accessor():

    def __init__(self, name:str, manager:Manager.Manager, version:"Version.Version", file_type_arguments:Any) -> None:
        self.name = name
        self.manager = manager
        self.version = version
        self.initialize()

    def initialize(self) -> None:
        pass

    def modify_file_name(self, file_name:str="") -> str:
        return file_name

    def trim_file_name(self, file_name:str) -> str:
        return file_name

    def install_all(self, destination:Path|None) -> None:
        return self.manager.install_all(destination)

    def file_exists(self, name:str) -> bool:
        return self.manager.file_exists(self.modify_file_name(name))

    def get_files_in(self, parent:str) -> list[str]:
        return [self.trim_file_name(file) for file in self.manager.get_files_in(self.modify_file_name(parent))]

    def get_file_list(self) -> list[str]:
        return [self.trim_file_name(file) for file in self.manager.get_files_in(self.modify_file_name())]

    def get_full_file_list(self) -> list[str]:
        return self.manager.get_file_list()

    @overload
    def read(self, file_name:str, mode:Literal["b"]) -> bytes: ...
    @overload
    def read(self, file_name:str, mode:Literal["t"]) -> str: ...
    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        return self.manager.read(self.modify_file_name(file_name), mode)

    def get_file(self, file_name:str, mode:Literal["b", "t"]="b") -> FileManager.FilePromise:
        return self.manager.get_file(self.modify_file_name(file_name), mode)

    def all_done(self) -> None:
        return self.manager.all_done()

class ScriptedAccessor(Accessor):

    def __new__(cls, *args, **kwargs) -> Self:
        def make_the_function(self: Self, func:Callable) -> Callable:
            # print(self, func, attribute, args, kwargs)
            return lambda *function_arguments, **function_keyword_arguments: func(self, *function_arguments, **function_keyword_arguments)
        output = super().__new__(cls)
        for attribute in cls.__dict__:
            attr = getattr(output, attribute)
            if not attribute.startswith("__") and hasattr(attr, "__call__") and not isinstance(attr, type):
                setattr(output, attribute, make_the_function(output, attr))
        return output
