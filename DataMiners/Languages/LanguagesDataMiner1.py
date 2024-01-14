import json

import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class LanguagesDataMiner1(LanguagesDataMiner.LanguagesDataMiner):

    def initialize(self, **kwargs) -> None:
        if "languages_location" in kwargs:
            self.languages_location = kwargs["languages_location"]
        else:
            raise ValueError("`LanguagesDataMiner1` was initialized without kwarg \"languages_location\"!")

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.LanguagesTypedDict]:
        resource_packs = dependency_data["resource_packs"]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        languages_files = {self.languages_location % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        languages_files_request = [(resource_pack_file, "t", json.load) for resource_pack_file in languages_files.keys()]
        files:dict[str,list[str]] = {key: value for key, value in self.read_files(languages_files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"languages.json\" files found in \"%s\"" % self.version)
        
        languages:dict[str,DataMinerTyping.LanguagesTypedDict] = {}
        for resource_pack_file, resource_pack_languages in files.items():
            resource_pack_name = languages_files[resource_pack_file]
            this_resource_pack_codes:set[str] = set()
            for language_code in resource_pack_languages:
                if language_code in this_resource_pack_codes:
                    raise RuntimeError("Duplicate language code \"%s\" in \"%s\" of \"%s\"." % (language_code, resource_pack_name, self.version.name))
                if language_code in languages:
                    languages[language_code]["defined_in"].append(resource_pack_name)
                else:
                    languages[language_code] = ({"code": language_code, "defined_in": [resource_pack_name], "properties": {}})
                    # `properties` is empty on purpose, so it can remain supportable by whatever uses this data.
                this_resource_pack_codes.add(language_code)

        
        return sorted(list(languages.values()), key=lambda x: x["code"])
