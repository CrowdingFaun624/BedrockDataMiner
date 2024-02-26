import pyjson5 # supports comments

import DataMiners.LoadingTips.LoadingTipsDataMiner as LoadingTipsDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class LoadingTipsDataMiner0(LoadingTipsDataMiner.LoadingTipsDataMiner):

    def initialize(self, **kwargs) -> None:
        if "loading_tips_locations" in kwargs:
            self.loading_tips_locations = kwargs["loading_tips_locations"]
        else:
            raise ValueError("`LoadingTipsDataMiner0` was initialized without kwarg \"loading_tips_locations\"!")

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.LoadingTips:
        resource_packs = dependency_data["resource_packs"]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for loading_tips_location in self.loading_tips_locations:
            resource_pack_files.update({loading_tips_location % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names})
        files_request = [(resource_pack_file, "t", pyjson5.load) for resource_pack_file in resource_pack_files.keys()]
        files:DataMinerTyping.LoadingTips = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"loading_tips.json\" files found in \"%s\"" % self.version)
        
        output = {resource_pack_files[resource_pack_file]: loading_tips for resource_pack_file, loading_tips in files.items()}
        return Sorting.sort_everything(output)
