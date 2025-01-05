import Component.Field.Field as Field
import Domain.Domain as Domain


class SerializerTypeField(Field.Field):

    __slots__ = (
        "serializer_type",
    )

    def __init__(self, serializer_name:str, domain:"Domain.Domain", path: list[str | int]) -> None:
        '''
        :serializer_name: The name of the Serializer referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.serializer_type = domain.serializer_classes[serializer_name]
