from typing import TypeVar

a = TypeVar("a")
b = TypeVar("b")

def sort_everything(data:a) -> a:
        '''Sorts the parent dictionary and all subdictionaries (recursive).'''
        if isinstance(data, list):
            output = []
            for item in data:
                output.append(sort_everything(item))
            return output
        elif isinstance(data, dict):
            return {key: sort_everything(value) for key, value in sorted(data.items())}
        else:
            return data

def sort_dict(data:dict[a,b]) -> dict[a,b]:
    return {key: value for key, value in sorted(data.items())}
