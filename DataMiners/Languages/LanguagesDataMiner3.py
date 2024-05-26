import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner


class LanguagesDataMiner3(LanguagesDataMiner.LanguagesDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.LanguagesTypedDict]:
        language_files = [file.split("/")[-1] for file in self.get_accessor("client").get_file_list() if file.startswith("lang")]
        if len(language_files) == 0:
            raise FileNotFoundError("No language files found in \"%s\"!" % self.version.name)
        language_codes = [language_file.split(".")[0] for language_file in language_files]
        languages:list[DataMinerTyping.LanguagesTypedDict] = [{"code": language_code, "defined_in": [], "properties": {}} for language_code in language_codes]
        return sorted(languages, key=lambda x: x["code"])
