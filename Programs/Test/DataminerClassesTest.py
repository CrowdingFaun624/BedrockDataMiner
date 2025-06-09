import traceback
from collections import defaultdict
from typing import TYPE_CHECKING

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerCollection import DataminerCollection
from Dataminer.Dataminers import run as dataminers_run
from Programs.Test.TestUtil import Plan
from Structure.StructureEnvironment import EnvironmentType, StructureEnvironment
from Version.Version import Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

type DataminerClass = type[Dataminer]

class DataminerClassPlan(Plan[DataminerClass]):

    label = "Dataminer classes"
    __slots__ = (
        "dataminer_classes",
    )

    def __init__(
        self,
        versions: list[Version],
        all_dataminer_collections: list[AbstractDataminerCollection],
        version_objects: dict[Version, set[DataminerClass]],
        domain:"Domain.Domain",
    ) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects, domain)
        dataminer_classes:defaultdict[DataminerClass,set[AbstractDataminerCollection]] = defaultdict(lambda: set())
        version = versions[-1]
        for dataminer_collection in all_dataminer_collections:
            if dataminer_collection.supports_version(version) and isinstance(dataminer_collection, DataminerCollection):
                dataminer_classes[dataminer_collection.get_dataminer_class(version)].add(dataminer_collection)
        self.dataminer_classes = {dataminer_class: sorted(dataminer_collections, key=lambda item: item.name) for dataminer_class, dataminer_collections in dataminer_classes.items()}

    def test(self) -> list[DataminerClass]:
        version = self.versions[-1]
        dataminer_collections:list[AbstractDataminerCollection] = []
        for dataminer_class in self.items_to_test:
            for dataminer_collection in self.dataminer_classes[dataminer_class]:
                if dataminer_collection.supports_version(version):
                    dataminer_collections.append(dataminer_collection)
                    break
            else:
                assert False
        print(f"Scanning {len(dataminer_collections)} DataminerCollections in {version}")
        structure_environment = StructureEnvironment(EnvironmentType.checking_types, self.domain)
        failed_dataminer_classes:list[DataminerClass] = []
        for dataminer_collection, exception in dataminers_run(version, dataminer_collections, structure_environment, recalculate_everything=True, print_messages=False):
            print(f"{dataminer_collection} on {version}")
            if exception is not None:
                traceback.print_exception(exception)
            if isinstance(dataminer_collection, DataminerCollection):
                failed_dataminer_classes.append(dataminer_collection.get_dataminer_class(version))
        return failed_dataminer_classes

    @classmethod
    def get_obj(cls, dataminer_collection: DataminerCollection, version: Version) -> DataminerClass:
        return dataminer_collection.get_dataminer_class(version)

    @classmethod
    def sort(cls, item: DataminerClass) -> "SupportsRichComparison":
        return item.__name__

    @classmethod
    def get_name(cls, item: DataminerClass) -> str:
        return item.__name__
