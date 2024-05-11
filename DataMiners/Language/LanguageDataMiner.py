import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class LanguageDataMiner(DataMiner.DataMiner):

    def combine_lines(self, lines:list[str]) -> list[str]:
        output:list[str] = []
        for line in lines:
            line = line.lstrip("\ufeff")
            if len(line.lstrip()) == 0:
                continue
            if line.lstrip().startswith("#") or len(line) == 0:
                continue
            if "=" in line:
                output.append(line)
            else:
                output[-1] += "\n" + line
        return output

    def process_line(self, line:str) -> tuple[str|None, DataMinerTyping.LanguageTypedDict|None]:
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

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Language:
        return super().activate(dependency_data)
