import traceback
from typing import TYPE_CHECKING

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Dataminer.Dataminers as Dataminers
import Programs.Test.TestUtil as TestUtil
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataminerCollectionPlan(TestUtil.Plan[AbstractDataminerCollection.AbstractDataminerCollection]):

    label = "DataminerCollections"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[AbstractDataminerCollection.AbstractDataminerCollection], version_objects: dict[Version.Version, set[AbstractDataminerCollection.AbstractDataminerCollection]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        self.dataminer_collections = version_objects[versions[-1]]

    def test(self) -> list[AbstractDataminerCollection.AbstractDataminerCollection]:
        version = self.versions[-1]
        print(f"Scanning {len(self.items_to_test)} DataminerCollections in {version}")
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failures = Dataminers.run(version, self.items_to_test, structure_environment, recalculate_everything=True, print_messages=False)
        failed_dataminer_collections:list[AbstractDataminerCollection.AbstractDataminerCollection] = []
        for dataminer_collection, exception in failures:
            print(f"{dataminer_collection} on {version}")
            if exception is not None:
                traceback.print_exception(exception)
            failed_dataminer_collections.append(dataminer_collection)
        return failed_dataminer_collections

    @classmethod
    def get_obj(cls, dataminer_collection: AbstractDataminerCollection.AbstractDataminerCollection, version: Version.Version) -> AbstractDataminerCollection.AbstractDataminerCollection:
        return dataminer_collection

    @classmethod
    def sort(cls, item: AbstractDataminerCollection.AbstractDataminerCollection) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: AbstractDataminerCollection.AbstractDataminerCollection) -> str:
        return item.name
