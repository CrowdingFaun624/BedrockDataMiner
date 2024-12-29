__all__ = ["uniforms_normalize"]

def uniforms_normalize(data:dict[str,str]) -> dict[str,str]|None:
    if "Name" in data:
        return
    assert len(data) == 1
    key = list(data.keys())[0]
    value = data[key]
    return {"Name": key, "Type": value}
