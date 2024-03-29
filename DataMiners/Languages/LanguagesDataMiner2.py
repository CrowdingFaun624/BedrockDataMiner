import json

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner

class LanguagesDataMiner2(LanguagesDataMiner.LanguagesDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "languages_location": (str, True),
    })

    def initialize(self, **kwargs) -> None:
        self.languages_location = kwargs["languages_location"]

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
