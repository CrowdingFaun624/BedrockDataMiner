from itertools import takewhile
from typing import Iterable, NotRequired, TypedDict

from Serializer.Serializer import Serializer

__all__ = ("LanguageSerializer",)

class LanguageObject(TypedDict):
    value: str
    comment: NotRequired[str]

class LanguageSerializer(Serializer[dict[str,LanguageObject]]):

    empty_okay = True

    def combine_lines(self, lines:list[str]) -> Iterable[str]:
        current_str:str|None = None
        for line in lines:
            line = line.lstrip("\ufeff")
            if len(line.lstrip()) == 0:
                continue
            if line.lstrip().startswith("#") or len(line) == 0:
                continue
            if current_str is None:
                current_str = line
                continue
            if "=" in line:
                yield current_str
                current_str = line
            else:
                current_str += "\n" + line

    def process_line(self, line:str) -> tuple[str|None, LanguageObject|None]:
        line = line.lstrip("\ufeff")
        if len(line.lstrip()) == 0:
            return None, None # empty line
        if line.lstrip().startswith("#") or len(line) == 0:
            return None, None # comment-only line, which I don't care about.
        if "##" in line:
            key_value, comment = line.split("##", maxsplit=1)
        else:
            key_value = line
            comment = None
        key_value = key_value.rstrip("\t")
        key, value = key_value.split("=", maxsplit=1)
        if value.endswith("\t#"):
            value = value.removesuffix("\t#").lstrip("\t")
        if comment is not None:
            octothorpe_count = sum(1 for octothorpe in takewhile(lambda char: char == "#", comment))
            comment = comment[octothorpe_count:].lstrip() # I will destory ALL OCTOTHORPES HAHAHAHAHAHAHAaaAAAA
        if comment is None:
            return key, {"value": value}
        else:
            return key, {"comment": comment, "value": value}

    def deserialize(self, data: bytes) -> dict[str, LanguageObject]:
        output:dict[str,LanguageObject] = {}
        lines = self.combine_lines(data.decode().splitlines())
        for line in lines:
            key, line_data = self.process_line(line)
            if key is None or line_data is None: continue
            output[key] = line_data
        return output
