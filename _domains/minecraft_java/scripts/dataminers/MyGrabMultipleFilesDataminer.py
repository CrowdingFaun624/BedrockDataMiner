from typing import Any

from Component.ComponentFunctions import component_function
from Dataminer.BuiltIns.GrabMultipleFilesDataminer import GrabMultipleFilesDataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.File import File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

give_me_the_parameters_please = GrabMultipleFilesDataminer.parameters
assert give_me_the_parameters_please is not None

@component_function()
class MyGrabMultipleFilesDataminer(GrabMultipleFilesDataminer):

    __slots__ = (
        "insert_namespace",
    )

    parameters = give_me_the_parameters_please.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("insert_namespace", False, (str, type(None))),
    ))

    def initialize(self, insert_namespace:str|None=None, **kwargs:Any) -> None:
        super().initialize(**kwargs)
        self.insert_namespace = insert_namespace

    def get_output(self, files: dict[tuple[str, str], bytes], accessor: DirectoryAccessor, environment: DataminerEnvironment) -> dict[str, File]|dict[str,dict[str,File]]:
        super_output = super().get_output(files, accessor, environment)
        if self.insert_namespace is not None:
            return {self.insert_namespace: super_output}
        else:
            return super_output
