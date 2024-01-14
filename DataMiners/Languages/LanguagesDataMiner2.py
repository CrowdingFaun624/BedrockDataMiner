import json

import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class LanguagesDataMiner2(LanguagesDataMiner.LanguagesDataMiner):

    def initialize(self, **kwargs) -> None:
        if "languages_location" in kwargs:
            self.languages_location = kwargs["languages_location"]
        else:
            raise ValueError("`LanguagesDataMiner1` was initialized without kwarg \"languages_location\"!")

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.LanguagesTypedDict]:
        if not self.file_exists(self.languages_location):
            raise FileNotFoundError("Language file \"%s\" does not exist in \"%s\"!" % (self.languages_location, self.version.name))
        language_file:list[str] = json.loads(self.read_file(self.languages_location, "t"))
        languages:list[DataMinerTyping.LanguagesTypedDict] = []
        already_codes:set[str] = set()
        for language_code in language_file:
            if language_code in already_codes:
                raise RuntimeError("Duplicate language code \"%s\" in \"%s\"." % (language_code, self.version.name))
            languages.append({"code": language_code, "defined_in": [], "properties": {}})
            already_codes.add(language_code)

        return sorted(languages, key=lambda x: x["code"])
