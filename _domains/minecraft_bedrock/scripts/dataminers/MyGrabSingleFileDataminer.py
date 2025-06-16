from typing import Any

from Component.ComponentFunctions import component_function
from Dataminer.BuiltIns.GrabSingleFileDataminer import GrabSingleFileDataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Utilities.File import File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


@component_function()
class MyGrabSingleFileDataminer(GrabSingleFileDataminer):

    __slots__ = (
        "insert_file_name",
        "insert_pack",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, str),
        TypedDictKeyTypeVerifier("insert_pack", False, str),
        TypedDictKeyTypeVerifier("insert_file_name", False, str),
    )

    def initialize(self, location:str, insert_pack:str|None=None, insert_file_name:str|None=None) -> None:
        super().initialize(location)
        self.insert_pack = insert_pack
        self.insert_file_name = insert_file_name

    def get_output(self, file: bytes, file_name:str, environment: DataminerEnvironment) -> File|Any:
        file_data = self.export_file(file, file_name)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        if self.insert_file_name is not None:
            file_data = {self.insert_file_name: file_data}
        return file_data
