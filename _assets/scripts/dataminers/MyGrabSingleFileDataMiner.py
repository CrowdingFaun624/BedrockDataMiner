from typing import Any

import DataMiner.BuiltIns.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MyGrabSingleFileDataMiner"]

class MyGrabSingleFileDataMiner(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, locations:list[str], insert_pack:str|None=None) -> None:
        super().initialize(locations)
        self.insert_pack = insert_pack

    def get_output(self, file: bytes, file_name:str, environment: DataMinerEnvironment.DataMinerEnvironment) -> File.File|Any:
        if self.insert_pack is not None:
            file_data = {self.insert_pack: self.export_file(file, file_name)}
        return file_data
