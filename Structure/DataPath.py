from types import EllipsisType, TracebackType
from typing import Any, Hashable, Literal, Self, TypedDict

from Component.Types import register_decorator
from Utilities.CustomJson import Coder
from Utilities.Exceptions import DataPathEmbeddedDataError

DataPathJsonTypedDict = TypedDict("DataPathJsonTypedDict", {"$special_type": Literal["data_path"], "root": str, "path_items":list[Any], "embedded_data": Any|None})

class DataPathCoder(Coder[DataPathJsonTypedDict, "DataPath"]):

    __slots__ = ()

    special_type_name = "data_path"

    @classmethod
    def decode(cls, data:DataPathJsonTypedDict) -> "DataPath":
        return DataPath(data["path_items"], data["root"], data["embedded_data"])

    @classmethod
    def encode(cls, data:"DataPath") -> DataPathJsonTypedDict:
        return {"$special_type": "data_path", "path_items": data.path_items, "root": data.root, "embedded_data": data.embedded_data}

@register_decorator(None, ..., json_coder=DataPathCoder)
class DataPath[K:Hashable, V]():
    """
    :param path_items: Items in the DataPath. Cannot contain None.
    :param root: The dataminer/structure in which this DataPath originates.
    :param embedded_data: Data given to this DataPath when it reaches the correct tag.
    """

    __slots__ = (
        "embedded_data",
        "hash",
        "path_items",
        "root",
    )

    def __init__(self, path_items:list[K], root:str, embedded_data:Any|EllipsisType=...) -> None:
        self.path_items = path_items
        self.root = root
        self.embedded_data:V|EllipsisType = embedded_data
        self.hash = None

    def last_key(self) -> K:
        """
        Returns the key of the most recently appended item.
        """
        return self[-1]

    def remove_embedded_data(self) -> Self:
        """
        Removes the embedded data from this DataPath. Returns itself.
        """
        self.embedded_data = ...
        return self

    def copy(self, new_item:K|EllipsisType=...) -> "DataPath":
        """
        Returns a new DataPath with a copied `path_items` attribute.

        :param new_item: An optional item to append to the copied DataPath.
        """
        output = DataPath(self.path_items.copy(), self.root, self.embedded_data)
        if new_item is not ...:
            output.append(new_item)
        return output

    def append(self, new_item:K) -> Self:
        """
        Adds a new item to this DataPath. Returns itself.

        :param new_item: The item to add to the end of the DataPath.
        """
        self.path_items.append(new_item)
        self.hash = None
        return self

    def embed(self, item:V) -> Self:
        """
        Embeds data into this DataPath. Returns itself.
        Used to carry data from deep inside Structures out.

        :param item: The data to embed.
        """
        self.embedded_data = item
        return self

    def get_embedded_data(self) -> V:
        if self.embedded_data is ...:
            raise DataPathEmbeddedDataError(self)
        return self.embedded_data

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type:type[BaseException]|None, exc_value:BaseException, traceback:TracebackType) -> Self:
        self.path_items.pop()
        self.hash = None
        return self

    def __str__(self) -> str:
        return "".join(f"[{item}]" for item in self.path_items)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self.path_items)}; {"empty" if len(self.path_items) == 0 else self.last_key()}>"

    def __getitem__(self, index:int) -> K:
        return self.path_items[index]

    def __iter__(self) -> list[K]:
        return self.path_items

    def __len__(self) -> int:
        return len(self.path_items)

    def __hash__(self) -> int:
        if self.hash is None:
            self.hash = hash((self.root, tuple(self.path_items)))
        return self.hash

    def __eq__(self, other:"DataPath") -> bool:
        return (self.root, self.path_items) == (other.root, other.path_items)

    def __gt__(self, other:"DataPath") -> bool:
        return (self.root, self.path_items) > (other.root, other.path_items)

    def __lt__(self, other:"DataPath") -> bool:
        return (self.root, self.path_items) < (other.root, other.path_items)

    def __ge__(self, other:"DataPath") -> bool:
        return (self.root, self.path_items) >= (other.root, other.path_items)

    def __le__(self, other:"DataPath") -> bool:
        return (self.root, self.path_items) <= (other.root, other.path_items)
