__all__ = ["categories_normalize"]

def categories_normalize(data:dict[str,dict[str,str]]) -> dict[str,dict[str,dict[str,str]]]:
    output:dict[str,dict[str,dict[str,str]]] = {}
    for element_name, element in data.items():
        output[element_name] = {element["type"]: element}
    return output
