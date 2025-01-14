import json

import Serializer.Serializer as Serializer

__all__ = ["TextureListSerializer"]

class TextureListSerializer(Serializer.Serializer):
    '''
    I have made a situation in which two different formats must
    be squeezed into the same Serializer. oops.
    '''

    def deserialize(self, data: bytes) -> list[str]:
        data_str = data.decode()
        if data_str[0] == "[":
            return json.loads(data_str)
        else:
            return data_str.splitlines()
