from typing import Any

import DataMiner.BuiltIns.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MyGrabSingleFileDataMiner"]

class MyGrabSingleFileDataMiner(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_file_name", "a str", False, str),
    )

    def initialize(self, location:str, insert_pack:str|None=None, insert_file_name:str|None=None) -> None:
        super().initialize(location)
        self.insert_pack = insert_pack
        self.insert_file_name = insert_file_name

    def get_output(self, file: bytes, file_name:str, environment: DataMinerEnvironment.DataMinerEnvironment) -> File.File|Any:
        file_data = self.export_file(file, file_name)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        if self.insert_file_name is not None:
            file_data = {self.insert_file_name: file_data}
        return file_data
