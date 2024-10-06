import traceback
from typing import TYPE_CHECKING

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMiners as DataMiners
import DataMiner.DataMinerSettings as DataMinerSettings
import Structure.StructureEnvironment as StructureEnvironment
import Programs.Test.TestUtil as TestUtil
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataMinerSettingsPlan(TestUtil.Plan[DataMinerSettings.DataMinerSettings]):

    label = "DataMinerSettings"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[DataMinerCollection.DataMinerCollection], version_objects: dict[Version.Version, set[DataMinerSettings.DataMinerSettings]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        version = versions[-1]
        self.dataminer_settings:dict[DataMinerSettings.DataMinerSettings,DataMinerCollection.DataMinerCollection] = {}
        for dataminer_collection in all_dataminer_collections:
            dataminer_settings = dataminer_collection.get_dataminer_settings(version)
            if dataminer_settings.get_dataminer_class() is not DataMiner.NullDataMiner:
                self.dataminer_settings[dataminer_settings] = dataminer_collection

    def test(self, all_dataminer_collections: dict[str, DataMinerCollection.DataMinerCollection]) -> list[DataMinerSettings.DataMinerSettings]:
        dataminer_collections = [self.dataminer_settings[dataminer_settings] for dataminer_settings in self.items_to_test]
        version = self.versions[-1]
        print("Scanning %i DataMinerCollections in %r" % (len(self.items_to_test), version))
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failed_dataminer_settings:list[DataMinerSettings.DataMinerSettings] = []
        for dataminer_collection, exception in DataMiners.run(version, dataminer_collections, structure_environment, all_dataminer_collections, recalculate_everything=True, print_messages=False):
            print("%r on %r (getting data file failed)" % (dataminer_collection, version))
            traceback.print_exception(exception)
            failed_dataminer_settings.append(dataminer_collection.get_dataminer_settings(version))
        return failed_dataminer_settings

    @classmethod
    def get_obj(cls, dataminer_collection: DataMinerCollection.DataMinerCollection, version: Version.Version) -> DataMinerSettings.DataMinerSettings:
        return dataminer_collection.get_dataminer_settings(version)

    @classmethod
    def sort(cls, item: DataMinerSettings.DataMinerSettings) -> "SupportsRichComparison":
        return item.get_name()

    @classmethod
    def get_name(cls, item: DataMinerSettings.DataMinerSettings) -> str:
        return "%s on %r" % (item.get_name(), item.version_range)
