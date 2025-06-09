import traceback
from typing import TYPE_CHECKING

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import NullDataminer
from Dataminer.DataminerCollection import DataminerCollection
from Dataminer.Dataminers import run as dataminers_run
from Dataminer.DataminerSettings import DataminerSettings
from Programs.Test.TestUtil import Plan
from Structure.StructureEnvironment import EnvironmentType, StructureEnvironment
from Version.Version import Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataminerSettingsPlan(Plan[DataminerSettings]):

    label = "DataminerSettings"
    __slots__ = (
        "dataminer_settings",
    )

    def __init__(
        self,
        versions: list[Version],
        all_dataminer_collections: list[AbstractDataminerCollection],
        version_objects: dict[Version, set[DataminerSettings]],
        domain:"Domain.Domain",
    ) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects, domain)
        version = versions[-1]
        self.dataminer_settings:dict[DataminerSettings,DataminerCollection] = {}
        for dataminer_collection in all_dataminer_collections:
            if not isinstance(dataminer_collection, DataminerCollection):
                continue
            dataminer_settings = dataminer_collection.get_dataminer_settings(version)
            if dataminer_settings.get_dataminer_class() is not NullDataminer:
                self.dataminer_settings[dataminer_settings] = dataminer_collection

    def test(self) -> list[DataminerSettings]:
        dataminer_collections = [self.dataminer_settings[dataminer_settings] for dataminer_settings in self.items_to_test]
        version = self.versions[-1]
        print(f"Scanning {len(self.items_to_test)} DataminerCollections in {version}")
        structure_environment = StructureEnvironment(EnvironmentType.checking_types, self.domain)
        failed_dataminer_settings:list[DataminerSettings] = []
        for dataminer_collection, exception in dataminers_run(version, dataminer_collections, structure_environment, recalculate_everything=True, print_messages=False):
            print(f"{dataminer_collection} on {version} (getting data file failed)")
            if exception is not None:
                traceback.print_exception(exception)
            if isinstance(dataminer_collection, DataminerCollection):
                failed_dataminer_settings.append(dataminer_collection.get_dataminer_settings(version))
        return failed_dataminer_settings

    @classmethod
    def get_obj(cls, dataminer_collection: DataminerCollection, version: Version) -> DataminerSettings:
        return dataminer_collection.get_dataminer_settings(version)

    @classmethod
    def sort(cls, item: DataminerSettings) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: DataminerSettings) -> str:
        return f"{item.name} on {item.version_range}"
