import pyjson5

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.LootTables.LootTablesDataMiner as LootTablesDataMiner
import Utilities.Sorting as Sorting

class LootTablesDataMiner0(LootTablesDataMiner.LootTablesDataMiner):

    def initialize(self, **kwargs) -> None:
        if "behavior_packs_location" in kwargs:
            self.behavior_packs_location:str|None = kwargs["behavior_packs_location"]
        else:
            raise ValueError("`LootTablesDataMiner0` was initialized without kwarg \"behavior_packs_location\"!")

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.LootTables:
        behavior_packs = dependency_data["behavior_packs"]
        loot_table_files:dict[tuple[str,str],str] = {}
        for behavior_pack in behavior_packs:
            behavior_path_loot_tables_path = "%s/%s/loot_tables/" % (self.behavior_packs_location, behavior_pack["name"])
            for loot_table_path in self.get_files_in(behavior_path_loot_tables_path):
                assert loot_table_path.endswith(".json")
                loot_table_name = loot_table_path.replace(behavior_path_loot_tables_path, "", 1).replace(".json", "", 1)
                assert not loot_table_name.endswith(".json")
                loot_table_files[loot_table_name, behavior_pack["name"]] = loot_table_path
        if len(loot_table_files) == 0:
            raise FileNotFoundError("No loot table files found in \"%s\"" % self.version)
        output:DataMinerTyping.LootTables = {}
        for (loot_table_name, behavior_pack_name), loot_table_path in loot_table_files.items():
            loot_table_data = pyjson5.loads(self.read_file(loot_table_path))
            if loot_table_name not in output:
                output[loot_table_name] = {behavior_pack_name: loot_table_data}
            else:
                output[loot_table_name][behavior_pack_name] = loot_table_data
        return Sorting.sort_everything(output)
