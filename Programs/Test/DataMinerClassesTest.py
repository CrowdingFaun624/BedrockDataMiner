import traceback
from collections import defaultdict
from typing import TYPE_CHECKING, TypeAlias

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMiners as DataMiners
import Structure.StructureEnvironment as StructureEnvironment
import Programs.Test.TestUtil as TestUtil
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

DataMinerClass:TypeAlias = type[DataMiner.DataMiner]

class DataMinerClassPlan(TestUtil.Plan[DataMinerClass]):

    label = "DataMiner classes"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[DataMinerCollection.DataMinerCollection], version_objects: dict[Version.Version, set[DataMinerClass]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        dataminer_classes:defaultdict[DataMinerClass,set[DataMinerCollection.DataMinerCollection]] = defaultdict(lambda: set())
        version = versions[-1]
        for dataminer_collection in all_dataminer_collections:
            if dataminer_collection.supports_version(version):
                dataminer_classes[dataminer_collection.get_dataminer_settings(version).get_dataminer_class()].add(dataminer_collection)
        self.dataminer_classes = {dataminer_class: sorted(dataminer_collections, key=lambda item: item.name) for dataminer_class, dataminer_collections in dataminer_classes.items()}

    def test(self, all_dataminer_collections:dict[str,DataMinerCollection.DataMinerCollection]) -> list[DataMinerClass]:
        version = self.versions[-1]
        dataminer_collections:list[DataMinerCollection.DataMinerCollection] = []
        for dataminer_class in self.items_to_test:
            for dataminer_collection in self.dataminer_classes[dataminer_class]:
                if dataminer_collection.supports_version(version):
                    dataminer_collections.append(dataminer_collection)
                    break
            else:
                assert False
        print("Scanning %i DataMinerCollections in %r" % (len(dataminer_collections), version))
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        failed_dataminer_classes:list[DataMinerClass] = []
        for dataminer_collection, exception in DataMiners.run(version, dataminer_collections, structure_environment, all_dataminer_collections, recalculate_everything=True, print_messages=False):
            print("%r on %r" % (dataminer_collection, version))
            traceback.print_exception(exception)
            failed_dataminer_classes.append(dataminer_collection.get_dataminer_settings(version).get_dataminer_class())
        return failed_dataminer_classes

    @classmethod
    def get_obj(cls, dataminer_collection: DataMinerCollection.DataMinerCollection, version: Version.Version) -> DataMinerClass:
        return dataminer_collection.get_dataminer_settings(version).get_dataminer_class()

    @classmethod
    def sort(cls, item: DataMinerClass) -> "SupportsRichComparison":
        return item.__name__

    @classmethod
    def get_name(cls, item: DataMinerClass) -> str:
        return item.__name__
