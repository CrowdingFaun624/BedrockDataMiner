import Structure.Difference as D

class Trace():

    def __init__(self, data:list[tuple[str,str|int|D.Diff|None]]|None=None, current_key:str|None=None) -> None:
        self.data = [] if data is None else data
        self.current_key = current_key

    def copy(self, name:str|None=None, key:str|int|D.Diff|None=None) -> "Trace":
        if name is None:
            return Trace(self.data.copy())
        else:
            new_trace = self.data.copy()
            new_trace.append((name, key))
            return Trace(new_trace)

    def give_key(self, current_key:str|int) -> "Trace":
        self.current_key = current_key
        return self

    def __str__(self) -> str:
        if self.current_key is None:
            return ".".join("%s[%s]" % (name, index) for name, index in self.data)
        else:
            if len(self.data) == 0:
                return str(self.current_key)
            else:
                return ".".join("%s[%s]" % (name, index) for name, index in self.data) + ".%s" % (self.current_key)
