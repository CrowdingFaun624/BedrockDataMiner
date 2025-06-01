import Domain.Domains as Domains
import Serializer.Serializer as Serializer
import Utilities.File as File

__all__ = ("normalize",)

domain = Domains.get_domain_from_module(__name__)
json_serializer = domain.script_referenceable.get_future("minecraft_common!serializers/json", Serializer.Serializer)

def normalize[a](data:dict[str,File.File[a]]) -> dict[str,a]:
    return {key: value.read(json_serializer.get()) for key, value in data.items()}
