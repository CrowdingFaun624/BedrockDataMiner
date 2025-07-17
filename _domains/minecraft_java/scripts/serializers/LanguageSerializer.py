# split from minecraft_bedrock's LanguageSerializer because there's no comments in JE

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


@component_function()
class LanguageSerializer(Serializer[dict[str,str]]):

    __slots__ = ()
    empty_okay = True

    def deserialize(self, data: bytes) -> dict[str, str]:
        # we check for number of "=" because 17w47a en_us.lang line 1778 is incomplete
        return dict(line.split("=", maxsplit=1) for line in data.decode().splitlines() if line != "" and line.count("=") >= 1)
