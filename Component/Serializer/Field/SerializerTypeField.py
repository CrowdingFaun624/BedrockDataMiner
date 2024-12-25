import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Serializer.CustomJsonSerializer as CustomJsonSerializer
import Serializer.DummySerializer as DummySerializer
import Serializer.JsonSerializer as JsonSerializer
import Serializer.LinesSerializer as LinesSerializer
import Serializer.RepairableJsonSerializer as RepairableJsonSerializer
import Serializer.Serializer as Serializer
import Serializer.TextSerializer as TextSerializer

BUILT_IN_SERIALIZER_CLASSES = {dataminer_class.__name__: dataminer_class for dataminer_class in [
    CustomJsonSerializer.CustomJsonSerializer,
    DummySerializer.DummySerializer,
    JsonSerializer.JsonSerializer,
    LinesSerializer.LinesSerializer,
    RepairableJsonSerializer.RepairableJsonSerializer,
    Serializer.Serializer,
    TextSerializer.TextSerializer,
]}

SERIALIZER_CLASSES = ScriptImporter.import_scripted_types("serializers/", BUILT_IN_SERIALIZER_CLASSES, Serializer.Serializer)

class SerializerTypeField(Field.Field):

    def __init__(self, serializer_name:str, path: list[str | int]) -> None:
        '''
        :serializer_name: The name of the Serializer referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.serializer = SERIALIZER_CLASSES[serializer_name]

    def get_final(self) -> type[Serializer.Serializer]:
        return self.serializer
