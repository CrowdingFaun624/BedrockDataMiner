import json

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class LanguagesDataMiner2(LanguagesDataMiner.LanguagesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("languages_location", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.languages_location:str = kwargs["languages_location"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.LanguagesTypedDict]:
        accessor = self.get_accessor("client")
        if not accessor.file_exists(self.languages_location):
            raise Exceptions.DataMinerNothingFoundError(self)
        language_file:list[str] = json.loads(accessor.read(self.languages_location, "t"))
        languages:list[DataMinerTyping.LanguagesTypedDict] = []
        already_codes:set[str] = set()
        for language_code in language_file:
            if language_code in already_codes:
                raise Exceptions.DataMinerFailureError(self, "Duplicate language code \"%s\"." % (language_code))
            languages.append({"code": language_code, "defined_in": [], "properties": {}})
            already_codes.add(language_code)

        return sorted(languages, key=lambda x: x["code"])
