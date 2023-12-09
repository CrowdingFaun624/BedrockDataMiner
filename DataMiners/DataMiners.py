import DataMiners.DataMiner as DataMiner

import DataMiners.Blocks.BlocksDataMiners as BlocksDataMiners
import DataMiners.ResourcePacks.ResourcePacksDataMiners as ResourcePacksDataMiners

dataminers:list[DataMiner.DataMinerCollection] = [
    BlocksDataMiners.dataminers,
    ResourcePacksDataMiners.dataminers,
]

def user_interface() -> None:
    import Downloader.VersionsParser as VersionsParser

    versions = VersionsParser.parse()
    version_names = {version.name: version for version in versions}
    version = None
    while version not in version_names:
        version = input("What version will be datamined? ")
    version = version_names[version]

    dataminer_names = {dataminer.name: dataminer for dataminer in dataminers}
    dataminer_collection = None
    while dataminer_collection not in dataminer_names or dataminer_collection == "*":
        dataminer_collection = input("What will be datamined (* for all)? %s " % str([dataminer.name for dataminer in dataminers]))
    if dataminer_collection == "*":
        dataminer_collections = dataminers
    else:
        dataminer_collections = [dataminer_names[dataminer_collection]]

    my_dataminers = [dataminer_collection.get_version(version) for dataminer_collection in dataminer_collections]
    for dataminer in my_dataminers:
        if isinstance(dataminer, DataMiner.NullDataMiner):
            print("Version %s does not have a dataminer for %s." % (dataminer.name, dataminer.version))
        else:
            dataminer.store()
            print("Successfully stored %s for %s." % (dataminer.file_name, dataminer.version))
