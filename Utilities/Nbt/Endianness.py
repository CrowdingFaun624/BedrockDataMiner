import enum

class End(enum.Enum):
    BIG = 0
    LITTLE = 1

class Endianness():

    BIG_CHAR = ">"
    LITTLE_CHAR = "<"

    def __init__(self, default:End=End.BIG, *, short:End|None=None, int:End|None=None, long:End|None=None, float:End|None=None, double:End|None=None) -> None:
        self.default = default
        self.short = (short if short is not None else default)
        self.int = (int if int is not None else default)
        self.long = (long if long is not None else default)
        self.float = (float if float is not None else default)
        self.double = (double if double is not None else default)

        self.short_char = self.get_char(self.short)
        self.int_char = self.get_char(self.int)
        self.long_char = self.get_char(self.long)
        self.float_char = self.get_char(self.float)
        self.double_char = self.get_char(self.double)

    def get_char(self, end:End) -> str:
        if end is End.BIG:
            return self.BIG_CHAR
        else:
            return self.LITTLE_CHAR

DEFAULT_ENDIANNESS = Endianness()
