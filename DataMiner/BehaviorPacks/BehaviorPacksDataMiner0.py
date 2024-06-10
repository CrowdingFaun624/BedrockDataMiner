import DataMiner.BehaviorPacks.BehaviorPacksDataMiner as BehaviorPacksDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class BehaviorPacksDataMiner0(BehaviorPacksDataMiner.BehaviorPacksDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("behavior_packs_directory", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.behavior_packs_directory:str = kwargs["behavior_packs_directory"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.BehaviorPackTypedDict]:
        behavior_pack_order = CollapseResourcePacks.resource_pack_order
        file_list = self.get_accessor("client").get_file_list()
        behavior_packs:list[DataMinerTyping.BehaviorPackTypedDict] = []
        behavior_pack_names:set[str] = set()

        for file in file_list:
            if file.startswith(self.behavior_packs_directory):
                if file.count("/") == 1: continue # random file in behavior packs directory, such as "flipbook_textures.json" in a0.16.0_build3
                name = file.split("/")[1]
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in behavior_pack_order:
                    raise Exceptions.UnrecognizedPackError(name, "behavior", self)
                if name in behavior_pack_names: continue # so they aren't recorded multiple times - wonky behavior
                behavior_pack_names.add(name)
                behavior_packs.append({"name": name, "path": "%s/%s/" % (self.behavior_packs_directory, name)})

        if len(behavior_packs) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return sorted(behavior_packs, key=lambda pack: behavior_pack_order[pack["name"]])
