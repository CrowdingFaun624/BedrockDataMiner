import pyjson5

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.TradeTables.TradeTablesDataMiner as TradeTablesDataMiner
import Utilities.Sorting as Sorting

class TradeTablesDataMiner0(TradeTablesDataMiner.TradeTablesDataMiner):

    def initialize(self, **kwargs) -> None:
        if "behavior_packs_location" in kwargs:
            self.behavior_packs_location:str|None = kwargs["behavior_packs_location"]
        else:
            raise ValueError("`TradeTablesDataMiner0` was initialized without kwarg \"behavior_packs_location\"!")

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.TradeTables:
        behavior_packs = dependency_data["behavior_packs"]
        trade_table_files:dict[tuple[str,str],str] = {}
        for behavior_pack in behavior_packs:
            behavior_path_trade_tables_path = "%s/%s/trading/" % (self.behavior_packs_location, behavior_pack["name"])
            for trade_table_path in self.get_files_in(behavior_path_trade_tables_path):
                assert trade_table_path.endswith(".json")
                trade_table_name = trade_table_path.replace(behavior_path_trade_tables_path, "", 1).replace(".json", "", 1)
                assert not trade_table_name.endswith(".json")
                trade_table_files[trade_table_name, behavior_pack["name"]] = trade_table_path
        if len(trade_table_files) == 0:
            raise FileNotFoundError("No trade table files found in \"%s\"" % self.version)
        output:DataMinerTyping.TradeTables = {}
        for (trade_table_name, behavior_pack_name), trade_table_path in trade_table_files.items():
            trade_table_data = pyjson5.loads(self.read_file(trade_table_path))
            if trade_table_name not in output:
                output[trade_table_name] = {behavior_pack_name: trade_table_data}
            else:
                output[trade_table_name][behavior_pack_name] = trade_table_data
        return Sorting.sort_everything(output)
