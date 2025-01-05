import traceback
from collections import defaultdict
from typing import TYPE_CHECKING

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Dataminer.Dataminers as Dataminers
import Programs.Test.TestUtil as TestUtil
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class StructurePlan(TestUtil.Plan[StructureBase.StructureBase]):

    label = "Structures"

    def __init__(self, versions: list[Version.Version], all_dataminer_collections: list[AbstractDataminerCollection.AbstractDataminerCollection], version_objects: dict[Version.Version, set[StructureBase.StructureBase]]) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects)
        version = versions[-1]
        structures:defaultdict[StructureBase.StructureBase,set[AbstractDataminerCollection.AbstractDataminerCollection]] = defaultdict(lambda: set())
        for dataminer_collection in all_dataminer_collections:
            if dataminer_collection.supports_version(version):
                structures[dataminer_collection.structure].add(dataminer_collection)
        self.structures = {structure: sorted(dataminer_collections, key=lambda item: item.name) for structure, dataminer_collections in structures.items()}

    def test(self) -> list[StructureBase.StructureBase]:
        version = self.versions[-1]
        dataminer_collections:list[AbstractDataminerCollection.AbstractDataminerCollection] = []
        for structure in self.items_to_test:
            for dataminer_collection in self.structures[structure]:
                if dataminer_collection.supports_version(version):
                    dataminer_collections.append(dataminer_collection)
                    break
            else:
                assert False
        print(f"Scanning {len(dataminer_collections)} DataminerCollections in {version}")
        dataminers_without_file:list[AbstractDataminerCollection.AbstractDataminerCollection] = []
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_types)
        printer_environment = StructureEnvironment.PrinterEnvironment(structure_environment, None, version, 0)
        failed_structures:list[StructureBase.StructureBase] = []
        for dataminer_collection in dataminer_collections:
            structure = dataminer_collection.structure
            try:
                data_file = dataminer_collection.get_data_file(version, non_exist_ok=True)
            except Exception as e:
                print(f"{dataminer_collection} on {structure} on {version} (getting data file failed)")
                traceback.print_exception(e)
                failed_structures.append(structure)
                continue
            if data_file is None:
                dataminers_without_file.append(dataminer_collection)
            else:
                # get all dataminer collections that already have files.
                try:
                    normalized_data = structure.normalize(data_file, printer_environment)
                    structure.check_types(normalized_data, structure_environment, (version,))
                except Exception as e:
                    print(f"{dataminer_collection} on {structure} on {version} (file was already datamined)")
                    traceback.print_exception(e)
                    failed_structures.append(structure)
        # get all remaining dataminer collections that didn't have files.
        for failed_dataminer, exception in Dataminers.run(version, dataminers_without_file, structure_environment, print_messages=False, recalculate_everything=False):
            print(f"{dataminer_collection} on {structure} on {version} (file was just datamined)")
            if exception is not None:
                traceback.print_exception(exception)
            failed_structures.append(failed_dataminer.structure)
        return failed_structures

    @classmethod
    def get_obj(cls, dataminer_collection: AbstractDataminerCollection.AbstractDataminerCollection, version: Version.Version) -> StructureBase.StructureBase:
        return dataminer_collection.structure

    @classmethod
    def sort(cls, item: StructureBase.StructureBase) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: StructureBase.StructureBase) -> str:
        return item.name
