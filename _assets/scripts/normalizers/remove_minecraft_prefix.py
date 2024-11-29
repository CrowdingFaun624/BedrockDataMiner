__all__ = ["remove_minecraft_prefix"]

def remove_minecraft_prefix(data:str) -> str:
    return data.removeprefix("minecraft:")
