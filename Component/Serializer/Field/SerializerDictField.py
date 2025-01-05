import Component.Field.FieldContainer as FieldContainer
import Component.Serializer.Field.SerializerField as SerializerField
import Serializer.Serializer as Serializer


class SerializerDictField(FieldContainer.FieldContainer):

    __slots__ = (
        "_final",
        "serializer_fields",
    )

    def __init__(self, serializers:dict[str,str], path: list[str | int]) -> None:
        self.serializer_fields = {key: SerializerField.SerializerField(serializer_name, path + [key]) for key, serializer_name in serializers.items()}
        self._final:dict[str,Serializer.Serializer]|None = None
        super().__init__(list(self.serializer_fields.values()), path)

    @property
    def final(self) -> dict[str,Serializer.Serializer]:
        if self._final is None:
            self._final = {key: serializer_field.subcomponent.final for key, serializer_field in self.serializer_fields.items()}
        return self._final
