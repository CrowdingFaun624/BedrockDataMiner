import Domain.Domain as Domain
import Utilities.FileManager as FileManager

domains:dict[str,Domain.Domain] = {directory.name: Domain.Domain(directory.name) for directory in FileManager.DOMAINS_DIRECTORY.iterdir()}

def get_domain_from_module(module_name:str) -> Domain.Domain:
    '''
    Can be used in a Domain's script to get the Domain it belongs to.
    :module_name: The name of the module, `__name__`.
    '''
    domain_name = module_name.split(".", maxsplit=2)[1]
    return domains[domain_name]
