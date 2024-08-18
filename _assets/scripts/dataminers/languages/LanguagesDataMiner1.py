import json

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.FileDataMiner as FileDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["LanguagesDataMiner1"]

class LanguagesDataMiner1(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("languages_location", "a str", True, str),
    )

    def initialize(self, languages_location:str) -> None:
        self.languages_location = languages_location

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.LanguagesTypedDict]:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        resource_pack_names = [(resource_pack["name"], resource_pack["path"]) for resource_pack in resource_packs]
        languages_files = {resource_pack_path + self.languages_location: resource_pack_name for resource_pack_name, resource_pack_path in resource_pack_names}
        languages_files_request = [(resource_pack_file, "t", json.load) for resource_pack_file in languages_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,list[str]] = {key: value for key, value in self.read_files(accessor, languages_files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        languages:dict[str,DataMinerTyping.LanguagesTypedDict] = {}
        for resource_pack_file, resource_pack_languages in files.items():
            resource_pack_name = languages_files[resource_pack_file]
            this_resource_pack_codes:set[str] = set()
            for language_code in resource_pack_languages:
                if language_code in this_resource_pack_codes:
                    raise Exceptions.DataMinerFailureError(self, "Duplicate language code \"%s\" in \"%s\"." % (language_code, resource_pack_name))
                if language_code in languages:
                    languages[language_code]["defined_in"].append(resource_pack_name)
                else:
                    languages[language_code] = ({"code": language_code, "defined_in": [resource_pack_name], "properties": {}})
                    # `properties` is empty on purpose, so it can remain supportable by whatever uses this data.
                this_resource_pack_codes.add(language_code)


        return sorted(list(languages.values()), key=lambda x: x["code"])
