import traceback
from typing import TYPE_CHECKING

import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMiners as DataMiners
import Structure.StructureEnvironment as StructureEnvironment
import Programs.Test.TestUtil as TestUtil
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataMinerCollectionPlan(TestUtil.Plan[DataMinerCollection.DataMinerCollection]):

    label = "DataMinerCollections"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[DataMinerCollection.DataMinerCollection], version_objects: dict[Version.Version, set[DataMinerCollection.DataMinerCollection]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        self.dataminer_collections = version_objects[versions[-1]]

    def test(self, all_dataminer_collections:dict[str,DataMinerCollection.DataMinerCollection]) -> list[DataMinerCollection.DataMinerCollection]:
        version = self.versions[-1]
        print("Scanning %i DataMinerCollections in %r" % (len(self.items_to_test), version))
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failures = DataMiners.run(version, self.items_to_test, structure_environment, all_dataminer_collections, recalculate_everything=True, print_messages=False)
        failed_dataminer_collections:list[DataMinerCollection.DataMinerCollection] = []
        for dataminer_collection, exception in failures:
            print("%r on %r" % (dataminer_collection, version))
            if exception is not None:
                traceback.print_exception(exception)
            failed_dataminer_collections.append(dataminer_collection)
        return failed_dataminer_collections

    @classmethod
    def get_obj(cls, dataminer_collection: DataMinerCollection.DataMinerCollection, version: Version.Version) -> DataMinerCollection.DataMinerCollection:
        return dataminer_collection

    @classmethod
    def sort(cls, item: DataMinerCollection.DataMinerCollection) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: DataMinerCollection.DataMinerCollection) -> str:
        return item.name
