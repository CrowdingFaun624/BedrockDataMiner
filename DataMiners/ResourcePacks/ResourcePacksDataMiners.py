import DataMiners.ResourcePacks.ResourcePacksDataMiner0 as ResourcePacksDataMiner0

# dataminers = DataMiner.DataMinerCollection("resource_packs.json", "resource_packs", ResourcePacksComparer.comparer, [
#     DataMiner.DataMinerSettings("a0.17.0.2", "-", ResourcePacksDataMiner0.ResourcePacksDataMiner0, resource_packs_folder="resource_packs"),
#     DataMiner.DataMinerSettings("a0.15.0_build1", "a0.17.0.2", ResourcePacksDataMiner0.ResourcePacksDataMiner0, resource_packs_folder="resourcepacks"),
#     # Prior to a0.15.0_build1, resource packs did not exist.
# ])

dataminers = [
    ResourcePacksDataMiner0.ResourcePacksDataMiner0,
]
