import DataMiners.BlocksClient.BlocksClientDataMiner0 as BlocksClientDataMiner0

# dataminers = DataMiner.DataMinerCollection("blocks_client.json", "blocks_client", BlocksClientComparer.comparer, [
#     DataMiner.DataMinerSettings("a0.17.0.2", "-", BlocksClientDataMiner0.BlocksClientDataMiner0, ["resource_packs"], blocks_locations=["resource_packs/%s/blocks.json"]),
#     DataMiner.DataMinerSettings("a0.15.0_build1", "a0.17.0.2", BlocksClientDataMiner0.BlocksClientDataMiner0, ["resource_packs"], blocks_locations=["resourcepacks/%s/blocks.json", "resourcepacks/%s/client/blocks.json"]),
#     # Prior to a0.15.0_build1, neither resource packs nor blocks.json existed.
# ])

dataminers = [
    BlocksClientDataMiner0.BlocksClientDataMiner0,
]
