from typing import Any

import Dataminer.BuiltIns.GrabSingleFileDataminer as GrabSingleFileDataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["MyGrabSingleFileDataminer"]

class MyGrabSingleFileDataminer(GrabSingleFileDataminer.GrabSingleFileDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_file_name", False, str),
    )

    def initialize(self, location:str, insert_pack:str|None=None, insert_file_name:str|None=None) -> None:
        super().initialize(location)
        self.insert_pack = insert_pack
        self.insert_file_name = insert_file_name

    def get_output(self, file: bytes, file_name:str, environment: DataminerEnvironment.DataminerEnvironment) -> File.File|Any:
        file_data = self.export_file(file, file_name)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        if self.insert_file_name is not None:
            file_data = {self.insert_file_name: file_data}
        return file_data
