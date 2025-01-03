from typing import Iterable, Iterator, Mapping


class TypeSet[T]():

    __slots__ = (
        "not_types",
        "types",
    )

    def __init__(self, types:Iterable[type[T]]|None=None) -> None:
        self.types:set[type[T]] = set(types) if types is not None else set()
        self.not_types:set[type] = set()

    def __iter__(self) -> Iterator[type[T]]:
        return iter(self.types)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {{{", ".join(contained_type.__name__ for contained_type in self.types)}}}>"

    def __contains__(self, _type:type[T]) -> bool:
        if _type in self.types: return True
        elif _type in self.not_types: return False
        else:
            for other_type in self.types:
                if issubclass(_type, other_type):
                    self.types.add(_type)
                    return True
            else:
                self.not_types.add(_type)
                return False

    def add(self, _type:type[T]) -> None:
        self.types.add(_type)
        self.not_types.discard(_type)

    def add_not(self, _type:type[T]) -> None:
        self.not_types.add(_type)
        self.types.discard(_type)

class TypeDict[T, A]():

    __slots__ = (
        "not_types",
        "types",
    )

    def __init__(self, types:Mapping[type[T], A]|None=None) -> None:
        self.types:dict[type[T],A] = dict(types) if types is not None else {}
        self.not_types:set[type] = set()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {{{", ".join(f"{contained_type.__name__}: {value}" for contained_type, value in self.types.items())}}}>"

    def __contains__(self, _type:type[T]) -> bool:
        if _type in self.types: return True
        elif _type in self.not_types: return False
        else:
            for other_type, value in self.types.items():
                if issubclass(_type, other_type):
                    self.types[_type] = value
                    return True
            else:
                self.not_types.add(_type)
                return False

    def __setitem__(self, _type:type[T], value:A) -> None:
        self.types[_type] = value
        self.not_types.discard(_type)

    def add_not(self, _type:type[T]) -> None:
        self.types.pop(_type, None)
        self.not_types.add(_type)

    def __getitem__(self, _type:type[T]) -> A:
        if (output := self.types.get(_type, ...)) is not ...:
            return output
        elif _type in self.not_types:
            raise KeyError(_type)
        else:
            for other_type, value in self.types.items():
                if issubclass(_type, other_type):
                    self.types[_type] = value
                    return value
            else:
                self.not_types.add(_type)
                raise KeyError(_type)

    def get[B](self, _type:type[T], default:B=None) -> A|B:
        if (output := self.types.get(_type, ...)) is not ...:
            return output
        elif _type in self.not_types:
            return default
        else:
            for other_type, value in self.types.items():
                if issubclass(_type, other_type):
                    self.types[_type] = value
                    return value
            else:
                self.not_types.add(_type)
                return default
