import Component.Field.FieldContainer as FieldContainer
import Component.Serializer.Field.SerializerField as SerializerField
import Serializer.Serializer as Serializer


class SerializerDictField(FieldContainer.FieldContainer):
    
    def __init__(self, serializers:dict[str,str], path: list[str | int]) -> None:
        self.serializer_fields = {key: SerializerField.SerializerField(serializer_name, path + [key]) for key, serializer_name in serializers.items()}
        super().__init__(list(self.serializer_fields.values()), path)
    
    def get_final(self) -> dict[str,Serializer.Serializer]:
        return {key: serializer_field.get_final() for key, serializer_field in self.serializer_fields.items()}
