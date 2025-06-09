from string import whitespace as py_whitespace

from Serializer.Serializer import Serializer

__all__ = ("LanguageSerializer",)

LEFT_WHITESPACE = "\ufeff" + py_whitespace
RIGHT_WHITESPACE = "#" + LEFT_WHITESPACE

class LanguageSerializer(Serializer[dict[str,str]]):

    __slots__ = ()
    empty_okay = True

    def combine_lines(self, lines:list[str]) -> list[str]:
        current_str:str|None = None
        output:list[str] = []
        for line in lines:
            line = line.lstrip(LEFT_WHITESPACE).rstrip(RIGHT_WHITESPACE)
            if len(line) == 0 or line.startswith("#"):
                continue
            elif current_str is None:
                current_str = line
                continue
            elif "=" in line:
                output.append(current_str)
                current_str = line
            else:
                current_str += "\n" + line
        if current_str is not None:
            output.append(current_str)
        return output

    def process_line(self, line:str) -> tuple[str|None, str|None]:
        if len(line) == 0 or line.startswith("#"):
            return None, None # empty line or comment-only line
        elif "##" in line:
            key_value = line.split("##", maxsplit=1)[0]
            key_value = key_value.rstrip("\t")
        else:
            key_value = line
        key, value = key_value.split("=", maxsplit=1)
        return key, value

    def deserialize(self, data: bytes) -> dict[str, str]:
        output:dict[str,str] = {}
        lines = self.combine_lines(data.decode().splitlines())
        for line in lines:
            key, value = self.process_line(line)
            if key is None or value is None: continue
            output[key] = value
        return output
