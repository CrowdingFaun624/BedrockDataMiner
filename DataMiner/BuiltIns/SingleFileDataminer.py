from typing import Any

import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.FileAccessor as FileAccessor
import Utilities.TypeVerifier as TypeVerifier


class SingleFileDataminer(FileDataminer.FileDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
    )

    def initialize(self, file_name:str) -> None:
        self.file_name = file_name

    def get_coverage(self, file_set: FileDataminer.FileSet, environment: DataminerEnvironment.DataminerEnvironment) -> set[str]:
        return {self.file_name}

    def activate(self, environment: DataminerEnvironment.DataminerEnvironment) -> Any:
        return self.export_file(self.get_accessor(FileAccessor.FileAccessor).read(), self.file_name)
