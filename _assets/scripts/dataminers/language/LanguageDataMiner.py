from typing import Iterable

import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping


def combine_lines(lines:list[str]) -> Iterable[str]:
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

def process_line(line:str) -> tuple[str|None, DataMinerTyping.LanguageTypedDict|None]:
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
