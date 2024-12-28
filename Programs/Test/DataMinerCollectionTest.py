import traceback
from typing import TYPE_CHECKING

import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import DataMiner.DataMiners as DataMiners
import Programs.Test.TestUtil as TestUtil
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataMinerCollectionPlan(TestUtil.Plan[AbstractDataMinerCollection.AbstractDataMinerCollection]):

    label = "DataMinerCollections"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[AbstractDataMinerCollection.AbstractDataMinerCollection], version_objects: dict[Version.Version, set[AbstractDataMinerCollection.AbstractDataMinerCollection]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        self.dataminer_collections = version_objects[versions[-1]]

    def test(self) -> list[AbstractDataMinerCollection.AbstractDataMinerCollection]:
        version = self.versions[-1]
        print(f"Scanning {len(self.items_to_test)} DataMinerCollections in {version}")
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failures = DataMiners.run(version, self.items_to_test, structure_environment, recalculate_everything=True, print_messages=False)
        failed_dataminer_collections:list[AbstractDataMinerCollection.AbstractDataMinerCollection] = []
        for dataminer_collection, exception in failures:
            print(f"{dataminer_collection} on {version}")
            if exception is not None:
                traceback.print_exception(exception)
            failed_dataminer_collections.append(dataminer_collection)
        return failed_dataminer_collections

    @classmethod
    def get_obj(cls, dataminer_collection: AbstractDataMinerCollection.AbstractDataMinerCollection, version: Version.Version) -> AbstractDataMinerCollection.AbstractDataMinerCollection:
        return dataminer_collection

    @classmethod
    def sort(cls, item: AbstractDataMinerCollection.AbstractDataMinerCollection) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: AbstractDataMinerCollection.AbstractDataMinerCollection) -> str:
        return item.name
