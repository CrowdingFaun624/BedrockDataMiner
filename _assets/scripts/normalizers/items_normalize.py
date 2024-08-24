from collections import defaultdict
from typing import Any, Iterable, TypeAlias, TypedDict, cast

__all__ = ["items_normalize"]

class ItemsType1(TypedDict):
    items: dict[str,dict[str,Any]]

ItemsType2:TypeAlias = dict[str,list[dict[str,str]]]

def iterate1(data:ItemsType1) -> Iterable[tuple[str, str, Any]]:
    for pack_name, items in cast(ItemsType1, data)["items"].items():
        for item_name, item in items.items():
            yield item_name, pack_name, item

def iterate2(data:ItemsType2) -> Iterable[tuple[str, str, Any]]:
    for pack_name, items in cast(ItemsType2, data).items():
        for item in items:
            item_name = item.pop("name")
            yield item_name, pack_name, item

def items_normalize(data:ItemsType1|ItemsType2) -> dict[str,dict[str,Any]]:
    output:defaultdict[str,dict[str,Any]] = defaultdict(lambda: {})
    if (list(data.values())[0], dict):
        iterator = iterate1(cast(ItemsType1, data))
    else:
        iterator = iterate2(cast(ItemsType2, data))
    for item_name, pack_name, item in iterator:
        output[item_name][pack_name] = item
    return dict(output)
