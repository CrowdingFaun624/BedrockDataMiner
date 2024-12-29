import traceback
from collections import defaultdict
from typing import TYPE_CHECKING

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerCollection as DataminerCollection
import Dataminer.Dataminers as Dataminers
import Programs.Test.TestUtil as TestUtil
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

type DataminerClass = type[Dataminer.Dataminer]

class DataminerClassPlan(TestUtil.Plan[DataminerClass]):

    label = "Dataminer classes"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[AbstractDataminerCollection.AbstractDataminerCollection], version_objects: dict[Version.Version, set[DataminerClass]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        dataminer_classes:defaultdict[DataminerClass,set[AbstractDataminerCollection.AbstractDataminerCollection]] = defaultdict(lambda: set())
        version = versions[-1]
        for dataminer_collection in all_dataminer_collections:
            if dataminer_collection.supports_version(version) and isinstance(dataminer_collection, DataminerCollection.DataminerCollection):
                dataminer_classes[dataminer_collection.get_dataminer_class(version)].add(dataminer_collection)
        self.dataminer_classes = {dataminer_class: sorted(dataminer_collections, key=lambda item: item.name) for dataminer_class, dataminer_collections in dataminer_classes.items()}

    def test(self) -> list[DataminerClass]:
        version = self.versions[-1]
        dataminer_collections:list[AbstractDataminerCollection.AbstractDataminerCollection] = []
        for dataminer_class in self.items_to_test:
            for dataminer_collection in self.dataminer_classes[dataminer_class]:
                if dataminer_collection.supports_version(version):
                    dataminer_collections.append(dataminer_collection)
                    break
            else:
                assert False
        print(f"Scanning {len(dataminer_collections)} DataminerCollections in {version}")
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failed_dataminer_classes:list[DataminerClass] = []
        for dataminer_collection, exception in Dataminers.run(version, dataminer_collections, structure_environment, recalculate_everything=True, print_messages=False):
            print(f"{dataminer_collection} on {version}")
            if exception is not None:
                traceback.print_exception(exception)
            if isinstance(dataminer_collection, DataminerCollection.DataminerCollection):
                failed_dataminer_classes.append(dataminer_collection.get_dataminer_class(version))
        return failed_dataminer_classes

    @classmethod
    def get_obj(cls, dataminer_collection: DataminerCollection.DataminerCollection, version: Version.Version) -> DataminerClass:
        return dataminer_collection.get_dataminer_class(version)

    @classmethod
    def sort(cls, item: DataminerClass) -> "SupportsRichComparison":
        return item.__name__

    @classmethod
    def get_name(cls, item: DataminerClass) -> str:
        return item.__name__
