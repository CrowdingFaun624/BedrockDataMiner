import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Dataminer.Dataminer as Dataminer


class OptionalDataminerTypeField(Field.Field):

    __slots__ = (
        "dataminer",
        "dataminer_name",
    )

    def __init__(self, dataminer_name:str|None, path: list[str | int]) -> None:
        '''
        :dataminer_name: The name of the Dataminer referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.dataminer_name = dataminer_name
        self.dataminer:type[Dataminer.Dataminer]


    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        self.dataminer = Dataminer.NullDataminer if self.dataminer_name is None else functions.dataminer_classes.get(self.dataminer_name, source_component, self.error_path)
        return [], []

    @property
    def exists(self) -> bool:
        "Returns True if this Field was initialized with a str, and False if it was initialized with None"
        return self.dataminer is not Dataminer.NullDataminer
