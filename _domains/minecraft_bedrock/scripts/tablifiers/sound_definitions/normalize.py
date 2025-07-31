from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import Serializer
from Utilities.File import File

domain = get_domain_from_module(__name__)
json_serializer = domain.script_referenceable.get_future("minecraft_common!serializers/json", Serializer)

@component_function(no_arguments=True, opens_files=True)
def normalize[a](data:dict[str,File[a]]) -> dict[str,a]:
    return {key: value.read(json_serializer.get()) for key, value in data.items()}
