import pyjson5

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Recipes.RecipesDataMiner as RecipesDataMiner
import Utilities.Sorting as Sorting

class RecipesDataMiner0(RecipesDataMiner.RecipesDataMiner):
    def initialize(self, **kwargs) -> None:
        if "behavior_packs_location" in kwargs:
            self.behavior_packs_location:str|None = kwargs["behavior_packs_location"]
        else:
            raise ValueError("`RecipesDataMiner0` was initialized without kwarg \"behavior_packs_location\"!")
    
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Recipes:
        behavior_packs = dependency_data["behavior_packs"]
        recipe_files:dict[tuple[str,str],str] = {}
        for behavior_pack in behavior_packs:
            behavior_path_items_path = "%s/%s/recipes/" % (self.behavior_packs_location, behavior_pack["name"])
            for recipe_path in self.get_files_in(behavior_path_items_path):
                assert recipe_path.endswith(".json")
                recipe_name = recipe_path.replace(behavior_path_items_path, "", 1).replace(".json", "", 1)
                assert not recipe_name.endswith(".json")
                recipe_files[recipe_name, behavior_pack["name"]] = recipe_path
        output:DataMinerTyping.Recipes = {}
        for (recipe_name, behavior_pack_name), recipe_path in recipe_files.items():
            recipe_data = pyjson5.loads(self.read_file(recipe_path))
            if recipe_name not in output:
                output[recipe_name] = {behavior_pack_name: recipe_data}
            else:
                output[recipe_name][behavior_pack_name] = recipe_data
        return Sorting.sort_everything(output)
