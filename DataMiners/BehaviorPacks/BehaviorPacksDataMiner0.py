import DataMiners.BehaviorPacks.BehaviorPacksDataMiner as BehaviorPacksDataMiner
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks


class BehaviorPacksDataMiner0(BehaviorPacksDataMiner.BehaviorPacksDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({"behavior_packs_folder": (str, True)})

    def initialize(self, **kwargs) -> None:
        self.behavior_packs_folder:str = kwargs["behavior_packs_folder"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.BehaviorPackTypedDict]:
        behavior_pack_order = CollapseResourcePacks.resource_pack_order
        file_list = self.get_accessor("client").get_file_list()
        behavior_packs:list[DataMinerTyping.BehaviorPackTypedDict] = []
        behavior_pack_names:set[str] = set()

        for file in file_list:
            assert not file.startswith("/") # just in case one of the InstallManagers goes wonky.
            if file.startswith(self.behavior_packs_folder):
                if file.count("/") == 1: continue # random file in behavior packs folder, such as "flipbook_textures.json" in a0.16.0_build3
                name = file.split("/")[1]
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in behavior_pack_order:
                    raise RuntimeError("Unknown behavior pack name in \"%s\": \"%s\"" % (self.version.name, name))
                if name in behavior_pack_names: continue # so they aren't recorded multiple times - wonky behavior
                behavior_pack_names.add(name)
                behavior_packs.append({"name": name, "path": "%s/%s/" % (self.behavior_packs_folder, name)})

        if len(behavior_packs) == 0:
            raise RuntimeError("No behavior packs found in \"%s\"!" % self.version.name)
        return sorted(behavior_packs, key=lambda pack: behavior_pack_order[pack["name"]])
