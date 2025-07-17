from typing import Any

from Component.ComponentFunctions import component_function
from Dataminer.BuiltIns.GrabSingleFileDataminer import GrabSingleFileDataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

give_me_the_parameters_please = GrabSingleFileDataminer.parameters
assert give_me_the_parameters_please is not None

@component_function()
class MyGrabSingleFileDataminer(GrabSingleFileDataminer):

    __slots__ = (
        "insert_file",
        "insert_namespace",
    )

    parameters = give_me_the_parameters_please.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("insert_namespace", False, (str, type(None))),
        TypedDictKeyTypeVerifier("insert_file", False, (str, type(None))),
    ))

    def initialize(self, insert_namespace:str|None=None, insert_file:str|None=None, **kwargs:Any) -> None:
        super().initialize(**kwargs)
        self.insert_namespace = insert_namespace
        self.insert_file = insert_file

    def get_output(self, file: bytes, file_name: str, environment: DataminerEnvironment) -> Any:
        output = super().get_output(file, file_name, environment)
        if self.insert_file is not None:
            output = {self.insert_file: output}
        if self.insert_namespace is not None:
            output = {self.insert_namespace: output}
        return output
