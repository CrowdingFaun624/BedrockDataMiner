import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern
import Component.Serializer.SerializerComponent as SerializerComponent
import Serializer.Serializer as Serializer

SERIALIZER_PATTERN:Pattern.Pattern[SerializerComponent.SerializerComponent] = Pattern.Pattern([{"is_serializer": True}])

class OptionalSerializerField(OptionalComponentField.OptionalComponentField[SerializerComponent.SerializerComponent]):
    
    def __init__(self, subcomponent_data:str|ComponentTyping.SerializerTypedDict|None, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, SERIALIZER_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_type="Serializer")

    def get_final(self) -> Serializer.Serializer|None:
        component = self.get_component()
        return component.get_final() if component is not None else None
