import json
from typing import IO, Any

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner
import Utilities.Exceptions as Exceptions


def decode(io:IO[bytes]) -> Any:
    # for decoding json files with foreign characters
    return json.loads(io.read().decode())

class LanguagesDataMiner0(LanguagesDataMiner.LanguagesDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.LanguagesTypedDict]:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        accessor = self.get_accessor("client")
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        languages_files = {"resource_packs/%s/texts/languages.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        languages_files_request = [(resource_pack_file, "t", json.load) for resource_pack_file in languages_files.keys()]
        language_file_contents:dict[str,list[str]] = {key: value for key, value in self.read_files(accessor, languages_files_request, non_exist_ok=True).items() if value is not None}
        if len(language_file_contents) == 0:
            raise Exceptions.DataMinerNothingFoundError(self, "(languages.json)")

        languages:dict[str,DataMinerTyping.LanguagesTypedDict] = {}
        for resource_pack_file, resource_pack_languages in language_file_contents.items():
            resource_pack_name = languages_files[resource_pack_file]
            this_resource_pack_codes:set[str] = set()
            for language_code in resource_pack_languages:
                if language_code in this_resource_pack_codes:
                    raise Exceptions.DataMinerFailureError(self, "Duplicate language code \"%s\" in \"%s\"." % (language_code, resource_pack_name))
                if language_code in languages:
                    languages[language_code]["defined_in"].append(resource_pack_name)
                else:
                    languages[language_code] = ({"code": language_code, "defined_in": [resource_pack_name], "properties": {}})
                this_resource_pack_codes.add(language_code)

        language_names_files = {"resource_packs/%s/texts/language_names.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        language_names_files_request = [(resource_pack_file, "b", decode) for resource_pack_file in language_names_files.keys()]
        language_names_file_contents:dict[str,list[list[str]]] = {key: value for key, value in self.read_files(accessor, language_names_files_request, non_exist_ok=True).items() if value is not None}
        if len(language_names_file_contents) == 0:
            raise Exceptions.DataMinerNothingFoundError(self, "(language_names.json)")

        for resource_pack_file, resource_pack_language_names in language_names_file_contents.items():
            resource_pack_name = language_names_files[resource_pack_file]
            for language_code, language_name in resource_pack_language_names:
                if language_code not in languages:
                    raise Exceptions.DataMinerFailureError(self, "Resource pack \"%s\" specifies language code \"%s\" (name \"%s\") in language_names.json, but that code is never defined in \"languages.json\"!" % (resource_pack_name, language_code, language_name))
                languages[language_code]["properties"][resource_pack_name] = {"name": language_name}

        return sorted(list(languages.values()), key=lambda x: x["code"])
