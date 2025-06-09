import traceback
from typing import TYPE_CHECKING

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminers import run as dataminers_run
from Programs.Test.TestUtil import Plan
from Structure.StructureEnvironment import EnvironmentType, StructureEnvironment
from Version.Version import Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class DataminerCollectionPlan(Plan[AbstractDataminerCollection]):

    label = "DataminerCollections"
    __slots__ = (
        "dataminer_collections",
    )

    def __init__(
        self,
        versions:list[Version],
        all_dataminer_collections: list[AbstractDataminerCollection],
        version_objects: dict[Version, set[AbstractDataminerCollection]],
        domain:"Domain.Domain",
    ) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects, domain)
        self.dataminer_collections = version_objects[versions[-1]]

    def test(self) -> list[AbstractDataminerCollection]:
        version = self.versions[-1]
        print(f"Scanning {len(self.items_to_test)} DataminerCollections in {version}")
        structure_environment = StructureEnvironment(EnvironmentType.checking_types, self.domain)
        failures = dataminers_run(version, self.items_to_test, structure_environment, recalculate_everything=True, print_messages=False)
        failed_dataminer_collections:list[AbstractDataminerCollection] = []
        for dataminer_collection, exception in failures:
            print(f"{dataminer_collection} on {version}")
            if exception is not None:
                traceback.print_exception(exception)
            failed_dataminer_collections.append(dataminer_collection)
        return failed_dataminer_collections

    @classmethod
    def get_obj(cls, dataminer_collection: AbstractDataminerCollection, version: Version) -> AbstractDataminerCollection:
        return dataminer_collection

    @classmethod
    def sort(cls, item: AbstractDataminerCollection) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: AbstractDataminerCollection) -> str:
        return item.name
