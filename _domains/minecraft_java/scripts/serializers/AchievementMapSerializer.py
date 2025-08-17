from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


@component_function()
class AchievementMapSerializer(Serializer):

    def deserialize(self, data: bytes) -> dict[int,str]:
        return {int(key): value for key, value in (item.split(",") for item in data.decode().splitlines())}
