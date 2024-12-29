import Domain.Domain as Domain

domains:dict[str,Domain.Domain] = {"minecraft_bedrock": Domain.Domain("minecraft_bedrock")}

def get_domain_from_module(module_name:str) -> Domain.Domain:
    '''
    Can be used in a Domain's script to get the Domain it belongs to.
    :module_name: The name of the module, `__name__`.
    '''
    return domains["minecraft_bedrock"]
