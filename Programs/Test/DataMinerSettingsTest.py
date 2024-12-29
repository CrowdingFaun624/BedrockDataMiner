import traceback
from typing import TYPE_CHECKING

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerCollection as DataminerCollection
import Dataminer.Dataminers as Dataminers
import Dataminer.DataminerSettings as DataminerSettings
import Programs.Test.TestUtil as TestUtil
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataminerSettingsPlan(TestUtil.Plan[DataminerSettings.DataminerSettings]):

    label = "DataminerSettings"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[AbstractDataminerCollection.AbstractDataminerCollection], version_objects: dict[Version.Version, set[DataminerSettings.DataminerSettings]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        version = versions[-1]
        self.dataminer_settings:dict[DataminerSettings.DataminerSettings,DataminerCollection.DataminerCollection] = {}
        for dataminer_collection in all_dataminer_collections:
            if not isinstance(dataminer_collection, DataminerCollection.DataminerCollection):
                continue
            dataminer_settings = dataminer_collection.get_dataminer_settings(version)
            if dataminer_settings.get_dataminer_class() is not Dataminer.NullDataminer:
                self.dataminer_settings[dataminer_settings] = dataminer_collection

    def test(self) -> list[DataminerSettings.DataminerSettings]:
        dataminer_collections = [self.dataminer_settings[dataminer_settings] for dataminer_settings in self.items_to_test]
        version = self.versions[-1]
        print(f"Scanning {len(self.items_to_test)} DataminerCollections in {version}")
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failed_dataminer_settings:list[DataminerSettings.DataminerSettings] = []
        for dataminer_collection, exception in Dataminers.run(version, dataminer_collections, structure_environment, recalculate_everything=True, print_messages=False):
            print(f"{dataminer_collection} on {version} (getting data file failed)")
            if exception is not None:
                traceback.print_exception(exception)
            if isinstance(dataminer_collection, DataminerCollection.DataminerCollection):
                failed_dataminer_settings.append(dataminer_collection.get_dataminer_settings(version))
        return failed_dataminer_settings

    @classmethod
    def get_obj(cls, dataminer_collection: DataminerCollection.DataminerCollection, version: Version.Version) -> DataminerSettings.DataminerSettings:
        return dataminer_collection.get_dataminer_settings(version)

    @classmethod
    def sort(cls, item: DataminerSettings.DataminerSettings) -> "SupportsRichComparison":
        return item.get_name()

    @classmethod
    def get_name(cls, item: DataminerSettings.DataminerSettings) -> str:
        return f"{item.get_name()} on {item.version_range}"
