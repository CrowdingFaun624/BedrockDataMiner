import pyjson5
from typing import Any

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Models.ModelsDataMiner as ModelsDataMiner
import Utilities.Sorting as Sorting

class ModelsDataMiner0(ModelsDataMiner.ModelsDataMiner):

    def initialize(self, **kwargs) -> None:
        if "resource_packs_location" in kwargs:
            self.resource_packs_location:str|None = kwargs["resource_packs_location"]
        else:
            raise ValueError("`ModelsDataMiner0` was initialized without kwarg \"resource_packs_location\"!")

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Models:
        resource_packs = dependency_data["resource_packs"]
        model_files:dict[tuple[str,str],str] = {}
        for resource_pack in resource_packs:
            resource_path_models_path = "%s/%s/models/" % (self.resource_packs_location, resource_pack["name"])
            for model_path in self.get_files_in(resource_path_models_path):
                assert model_path.endswith(".json")
                model_file_name = model_path.replace(resource_path_models_path, "", 1).replace(".json", "", 1)
                assert not model_file_name.endswith(".json")
                model_files[model_file_name, resource_pack["name"]] = model_path
        if len(model_files) == 0:
            raise FileNotFoundError("No model files found in \"%s\"" % self.version)
        
        output:DataMinerTyping.Models = {}
        for (model_name, resource_pack_name), model_path in model_files.items():
            model_data = pyjson5.loads(self.read_file(model_path))
            if model_name not in output:
                output[model_name] = {resource_pack_name: model_data}
            else:
                output[model_name][resource_pack_name] = model_data
        return Sorting.sort_everything(output)
