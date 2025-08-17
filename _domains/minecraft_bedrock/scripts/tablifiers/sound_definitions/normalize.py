from Component.ComponentFunctions import component_function
from Serializer.Serializer import SerializerCreator
from Utilities.File import File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, SerializerCreator),
))
def normalize[a](data:dict[str,File[a]], serializer:SerializerCreator) -> dict[str,a]:
    return {key: value.read(serializer.serializer) for key, value in data.items()}
