def get_domain_from_module(module_name:str) -> "Domain.Domain":
    '''
    Can be used in a Domain's script to get the Domain it belongs to.
    :module_name: The name of the module, `__name__`.
    '''
    domain_name = module_name.split(".", maxsplit=2)[1]
    return domains[domain_name]

def get_domain_name_from_module(module_name:str) -> str|None:
    '''
    Returns the name of the Domain from the name of the script module. If it is
    not a script (i.e. an internal file), return None.
    :module_name: The name of the module, `__name__`.
    '''
    module_split = module_name.split(".", maxsplit=2)
    return module_split[1] if module_split[0] == "_domains" else None

domains:dict[str,"Domain.Domain"] = {}

import Domain.Domain as Domain
from Utilities.FileManager import DOMAINS_DIRECTORY

domains.update((directory.name, Domain.Domain(directory.name)) for directory in DOMAINS_DIRECTORY.iterdir() if directory.joinpath("domain.json").exists())
for domain in domains.values():
    domain.link_domains(domains)
