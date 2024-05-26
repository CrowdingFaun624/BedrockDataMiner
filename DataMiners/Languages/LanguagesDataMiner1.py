import json

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Languages.LanguagesDataMiner as LanguagesDataMiner


class LanguagesDataMiner1(LanguagesDataMiner.LanguagesDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "languages_location": (str, True),
    })

    def initialize(self, **kwargs) -> None:
        self.languages_location:str = kwargs["languages_location"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.LanguagesTypedDict]:
        resource_packs = environment.dependency_data["resource_packs"]
        assert resource_packs is not None
        resource_pack_names = [(resource_pack["name"], resource_pack["path"]) for resource_pack in resource_packs]
        languages_files = {resource_pack_path + self.languages_location: resource_pack_name for resource_pack_name, resource_pack_path in resource_pack_names}
        languages_files_request = [(resource_pack_file, "t", json.load) for resource_pack_file in languages_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,list[str]] = {key: value for key, value in self.read_files(accessor, languages_files_request, non_exist_ok=True).items() if value is not None}
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
