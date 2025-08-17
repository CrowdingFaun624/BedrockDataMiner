import traceback
from collections import defaultdict
from typing import TYPE_CHECKING

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminers import run as dataminers_run
from Programs.Test.TestUtil import Plan
from Structure.StructureBase import StructureBase
from Structure.StructureEnvironment import (
    EnvironmentType,
    PrinterEnvironment,
    StructureEnvironment,
)
from Version.Version import Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

class StructurePlan(Plan[StructureBase]):

    label = "Structures"
    __slots__ = (
        "structures",
    )

    def __init__(
        self,
        versions: list[Version],
        all_dataminer_collections: list[AbstractDataminerCollection],
        version_objects: dict[Version, set[StructureBase]],
        domain:"Domain.Domain",
    ) -> None:
        super().__init__(versions, all_dataminer_collections, version_objects, domain)
        version = versions[-1]
        structures:defaultdict[StructureBase,set[AbstractDataminerCollection]] = defaultdict(lambda: set())
        for dataminer_collection in all_dataminer_collections:
            if dataminer_collection.supports_version(version):
                structures[dataminer_collection.structure].add(dataminer_collection)
        self.structures = {structure: sorted(dataminer_collections, key=lambda item: item.name) for structure, dataminer_collections in structures.items()}

    def test(self) -> list[StructureBase]:
        version = self.versions[-1]
        dataminer_collections:list[AbstractDataminerCollection] = []
        for structure in self.items_to_test:
            for dataminer_collection in self.structures[structure]:
                if dataminer_collection.supports_version(version):
                    dataminer_collections.append(dataminer_collection)
                    break
            else:
                assert False
        print(f"Scanning {len(dataminer_collections)} DataminerCollections in {version}")
        dataminers_without_file:list[AbstractDataminerCollection] = []
        structure_environment = StructureEnvironment(EnvironmentType.checking_types, self.domain)
        failed_structures:list[StructureBase] = []
        for dataminer_collection in dataminer_collections:
            printer_environment = PrinterEnvironment(structure_environment, dataminer_collection.get_structure_info(version), version, 0)
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
                    structure.type_check_from_raw(data_file, version, printer_environment)
                except Exception as e:
                    print(f"{dataminer_collection} on {structure} on {version} (file was already datamined)")
                    traceback.print_exception(e)
                    failed_structures.append(structure)
        # get all remaining dataminer collections that didn't have files.
        for failed_dataminer, exception in dataminers_run(version, dataminers_without_file, structure_environment, print_messages=False, recalculate_everything=False):
            print(f"{dataminer_collection} on {structure} on {version} (file was just datamined)")
            if exception is not None:
                traceback.print_exception(exception)
            failed_structures.append(failed_dataminer.structure)
        return failed_structures

    @classmethod
    def get_obj(cls, dataminer_collection: AbstractDataminerCollection, version: Version) -> StructureBase:
        return dataminer_collection.structure

    @classmethod
    def sort(cls, item: StructureBase) -> "SupportsRichComparison":
        return item.name

    @classmethod
    def get_name(cls, item: StructureBase) -> str:
        return item.full_name
