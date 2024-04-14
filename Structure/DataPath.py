from typing import Any, Hashable

class DataPath():

    def __init__(self, path_items:list[tuple[Hashable,type]], root:str, embedded_data:Any|None=None) -> None:
        '''
         * `path_items` cannot contain None.
         * `root` is the dataminer/structure in which this DataPath originates.
         * `embedded_data` is data given to this DataPath when it reaches the correct tag.'''
        self.path_items = path_items
        self.root = root
        self.embedded_data:Any|None = embedded_data
        self.hash = None

    def last_key(self) -> Hashable:
        return self[-1][0]

    def remove_embedded_data(self) -> "DataPath":
        self.embedded_data = None
        return self

    def copy(self, new_item:tuple[Hashable,type]|None=None) -> "DataPath":
        output = DataPath(self.path_items.copy(), self.root, self.embedded_data)
        if new_item is not None:
            output.append(new_item)
        return output

    def append(self, new_item:tuple[Hashable,type]) -> "DataPath":
        '''Item cannot be None'''
        self.path_items.append(new_item)
        self.hash = None
        return self

    def embed(self, item:Any) -> "DataPath":
        '''Used to extract data from within the structure.'''
        self.embedded_data = item
        return self

    def __str__(self) -> str:
        return "".join("[%s]" % (item) for item in self.path_items)

    def __repr__(self) -> str:
        return "<%s len %i; %s>" % (self.__class__.__name__, len(self.path_items), self.last_key())

    def __getitem__(self, index:int) -> tuple[Hashable,type]:
        return self.path_items[index]

    def __iter__(self) -> list[tuple[Hashable,type]]:
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
