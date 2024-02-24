import DataMiners.Recipes.RecipesDataMiner0 as RecipesDataMiner0

# dataminers = DataMiner.DataMinerCollection("recipes.json", "recipes", RecipesComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", RecipesDataMiner0.RecipesDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
# ])

dataminers = [
    RecipesDataMiner0.RecipesDataMiner0,
]
