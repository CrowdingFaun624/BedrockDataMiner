from typing import Iterable, Literal, TypedDict

import _domains.minecraft_bedrock.scripts.normalizers.collapse_resource_packs as collapse_resource_packs
import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["PacksDataminer"]

class PackTypedDict(TypedDict):
    name: str
    path: str

pack_order = collapse_resource_packs.resource_pack_order

class PacksDataminer(Dataminer.Dataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("directory", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)), function=lambda key, value: FileDataminer.location_value_function(key, value) if isinstance(value, str) else (True, "")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", True, TypeVerifier.EnumTypeVerifier({"resource", "behavior", "skin", "emote", "piece"})),
        TypeVerifier.TypedDictKeyTypeVerifier("subdirectory", False, str, function=FileDataminer.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("require_subdirectory", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("name_starts_with", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("care_about_packs_existing", False, bool)
    )

    def initialize(
        self,
        directory:str|list[str],
        pack_type:Literal["resource", "behavior", "skin", "emote", "piece"],
        subdirectory:str|None=None,
        require_subdirectory:bool=False,
        name_starts_with:str|None=None,
        care_about_packs_existing:bool=True,
    ) -> None:
        self.directory = [directory] if isinstance(directory, str) else directory
        self.pack_type:Literal["resource", "behavior", "skin", "emote", "piece"] = pack_type
        self.subdirectory = subdirectory
        self.require_subdirectory = require_subdirectory
        self.name_starts_with = name_starts_with
        self.care_about_packs_existing = care_about_packs_existing

    def do_file_pass(self, file_list:Iterable[str], unrecognized_packs:set[str], packs:list[PackTypedDict], pack_names:set[str], require_subdirectory:bool) -> None:
        for file in file_list:
            for directory in self.directory:
                if not file.startswith(directory): continue
                if file.count("/") == 1:
                    continue # random file in resource packs directory, such as "flipbook_textures.json" in a0.16.0_build3
                split_file = file.removeprefix(directory).split("/")
                name = split_file[0]
                if self.name_starts_with is not None and not name.startswith(self.name_starts_with):
                    continue
                has_subdirectory = self.subdirectory is not None and (len(split_file) >= 2 and split_file[1] + "/" == self.subdirectory)
                if self.subdirectory is not None and not has_subdirectory and require_subdirectory:
                    continue
                if name == "":
                    continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in pack_order and self.care_about_packs_existing:
                    unrecognized_packs.add(name)
                    continue
                if name in pack_names:
                    continue # so they aren't recorded multiple times - wonky behavior
                pack_names.add(name)
                if has_subdirectory:
                    path = f"{directory}{name}/{self.subdirectory}"
                else:
                    path = f"{directory}{name}/"
                packs.append({"name": name, "path": path})

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> list[PackTypedDict]:
        file_list:dict[str,str] = environment.dependency_data.get("all_files", self)
        packs:list[PackTypedDict] = []
        pack_names:set[str] = set()
        unrecognized_packs:set[str] = set()

        self.do_file_pass(file_list.keys(), unrecognized_packs, packs, pack_names, True)
        if self.subdirectory is not None and not self.require_subdirectory:
            # when subdirectory is not None, do a pass first requiring it
            # and then a pass not requiring it so the strictest path is
            # recorded.
            self.do_file_pass(file_list.keys(), unrecognized_packs, packs, pack_names, False)

        if len(unrecognized_packs) > 0 and self.care_about_packs_existing:
            raise collapse_resource_packs.UnrecognizedPackError(sorted(unrecognized_packs), self.pack_type, self)
        if len(packs) == 0:
            raise Exceptions.DataminerNothingFoundError(self)
        if self.care_about_packs_existing:
            packs.sort(key=lambda pack: pack_order[pack["name"]])
        return packs
