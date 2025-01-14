import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Serializer.Serializer as Serializer


class SerializerTypeField(Field.Field):

    __slots__ = (
        "serializer_name",
        "serializer_type",
    )

    def __init__(self, serializer_name:str, path: list[str | int]) -> None:
        '''
        :serializer_name: The name of the Serializer referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.serializer_name = serializer_name
        self.serializer_type:type[Serializer.Serializer]


    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        self.serializer_type = functions.serializer_classes.get(self.serializer_name, source_component, self.error_path)
        return [], []
