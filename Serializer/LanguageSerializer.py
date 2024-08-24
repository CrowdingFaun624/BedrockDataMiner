from typing import Iterable, TypedDict

from typing_extensions import NotRequired

import Serializer.Serializer as Serializer


class LanguageObject(TypedDict):
    value: str
    comment: NotRequired[str]

class LanguageSerializer(Serializer.Serializer[dict[str,LanguageObject],dict[str,LanguageObject]]):

    def serialize_json(self, data: dict[str, LanguageObject]) -> dict[str, LanguageObject]:
        return data # object is already in JSON-able form.

    def serialize(self, data:dict[str,LanguageObject]) -> bytes:
        return "\n".join("%s=%s\t##%s" % (key, item["value"], item["comment"]) if "comment" in item else "%s=%s" % (key, item["value"]) for key, item in data.items()).encode()

    def deserialize_json(self, data: dict[str, LanguageObject]) -> dict[str, LanguageObject]:
        return data

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
