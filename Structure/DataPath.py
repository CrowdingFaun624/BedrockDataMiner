from typing import Any, Hashable, Literal, TypedDict

from typing_extensions import Self

import Component.Types as Types
import Utilities.CustomJson as CustomJson

DataPathJsonTypedDict = TypedDict("DataPathJsonTypedDict", {"$special_type": Literal["data_path"], "root": str, "path_items":list[Any], "embedded_data": Any|None})

class DataPathCoder(CustomJson.Coder[DataPathJsonTypedDict, "DataPath"]):

    special_type_name = "data_path"

    @classmethod
    def decode(cls, data:DataPathJsonTypedDict) -> "DataPath":
        return DataPath(data["path_items"], data["root"], data["embedded_data"])

    @classmethod
    def encode(cls, data:"DataPath") -> DataPathJsonTypedDict:
        return {"$special_type": "data_path", "path_items": data.path_items, "root": data.root, "embedded_data": data.embedded_data}

@Types.register_decorator(None, hashing_method=hash, json_coder=DataPathCoder)
class DataPath():

    def __init__(self, path_items:list[Hashable], root:str, embedded_data:Any|None=None) -> None:
        '''
        :path_items: Items in the DataPath. Cannot contain None.
        :root: The dataminer/structure in which this DataPath originates.
        :embedded_data: Data given to this DataPath when it reaches the correct tag.'''
        self.path_items = path_items
        self.root = root
        self.embedded_data:Any|None = embedded_data
        self.hash = None

    def last_key(self) -> Hashable:
        '''Returns the key of the most recently appended item.'''
        return self[-1]

    def remove_embedded_data(self) -> Self:
        '''Removes the embedded data from this DataPath. Returns itself.'''
        self.embedded_data = None
        return self

    def copy(self, new_item:Hashable|None=None) -> "DataPath":
        '''
        Returns a new DataPath with a copied `path_items` attribute.
        :new_item: An optional item to append to the copied DataPath.
        '''
        output = DataPath(self.path_items.copy(), self.root, self.embedded_data)
        if new_item is not None:
            output.append(new_item)
        return output

    def append(self, new_item:Hashable) -> Self:
        '''
        Adds a new item to this DataPath. Returns itself.
        :new_item: The item to add to the end of the DataPath.
        '''
        self.path_items.append(new_item)
        self.hash = None
        return self

    def embed(self, item:Any) -> Self:
        '''
        Embeds data into this DataPath. Returns itself.
        Used to carry data from deep inside Structures out.
        :item: The data to embed.
        '''
        self.embedded_data = item
        return self

    def __str__(self) -> str:
        return "".join("[%s]" % (item) for item in self.path_items)

    def __repr__(self) -> str:
        return "<%s len %i; %s>" % (self.__class__.__name__, len(self.path_items), self.last_key())

    def __getitem__(self, index:int) -> Hashable:
        return self.path_items[index]

    def __iter__(self) -> list[Hashable]:
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
