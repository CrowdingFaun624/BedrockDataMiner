from typing import Literal, TypedDict

import _assets.scripts.normalizers.collapse_resource_packs.util as collapse_resource_packs
import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["PacksDataMiner"]

class PackTypedDict(TypedDict):
    name: str
    path: str

pack_order = collapse_resource_packs.resource_pack_order

class PacksDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("directory", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier({"resource", "behavior"})),
        TypeVerifier.TypedDictKeyTypeVerifier("subdirectory", "a str", False, (str, type(None)))
    )

    def initialize(self, directory:str, pack_type:Literal["resource", "behavior"], subdirectory:str|None=None) -> None:
        self.directory = directory
        self.pack_type:Literal["resource", "behavior"] = pack_type
        self.subdirectory = subdirectory

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[PackTypedDict]:
        file_list:list[str] = environment.dependency_data.get("all_files", self)
        packs:list[PackTypedDict] = []
        pack_names:set[str] = set()

        unrecognized_packs:set[str] = set()
        for file in file_list:
            if file.startswith(self.directory):
                if file.count("/") == 1: continue # random file in resource packs directory, such as "flipbook_textures.json" in a0.16.0_build3
                split_file = file.split("/")
                name = split_file[1]
                has_subdirectory = self.subdirectory is not None and (len(split_file) >= 3 and split_file[2] == self.subdirectory)
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in pack_order:
                    unrecognized_packs.add(name)
                    continue
                if name in pack_names: continue # so they aren't recorded multiple times - wonky behavior
                pack_names.add(name)
                if has_subdirectory:
                    path = "%s/%s/%s/" % (self.directory, name, self.subdirectory)
                else:
                    path = "%s/%s/" % (self.directory, name)
                packs.append({"name": name, "path": path})

        if len(unrecognized_packs) > 0:
            raise Exceptions.UnrecognizedPackError(sorted(unrecognized_packs), self.pack_type, self)
        if len(packs) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return sorted(packs, key=lambda pack: pack_order[pack["name"]])
