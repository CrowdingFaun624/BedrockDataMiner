import Comparison.Comparer as Comparer
import DataMiners.DataMiner as DataMiner
# import DataMiners.Recipes.RecipesComparer as RecipesComparer
import DataMiners.Recipes.RecipesDataMiner0 as RecipesDataMiner0

dataminers = DataMiner.DataMinerCollection("recipes.json", "recipes", Comparer.default_comparer, [
    DataMiner.DataMinerSettings("-", "-", RecipesDataMiner0.RecipesDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
])
