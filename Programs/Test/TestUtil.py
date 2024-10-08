from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Generic, Hashable, TypeVar

import Component.Importer as Importer
import DataMiner.DataMinerCollection as DataMinerCollection
import Version.Version as Version

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

def count_bits(number:int) -> int:
    return bin(number).count("1")

def get_overlapping_bits(all_bits:list[int], length:int) -> list[int]:
    '''
    Returns a subset of `bits` such that the bitwise-or-sum of the result has all bits activated.
    :bits: The list of bits.
    :length: The number of bits that must be activated.
    '''
    max_index:int|None = None
    max_count = 0
    for index, bits in enumerate(all_bits):
        if (count := count_bits(bits)) > max_count:
            max_count = count
            max_index = index
    assert max_index is not None
    current_bits = all_bits[max_index]
    indexes_used:set[int] = {max_index}
    # repeatedly find bits that when added, increase the coverage the most.
    while count_bits(current_bits) < length:
        max_index:int|None = None
        max_overlappedness = 0
        for index, bits in enumerate(all_bits):
            if index in indexes_used: continue
            overlappedness = count_bits(current_bits | bits)
            if overlappedness > max_overlappedness:
                max_overlappedness = overlappedness
                max_index = index
        assert max_index is not None
        current_bits = current_bits | all_bits[max_index]
        indexes_used.add(max_index)
    return [all_bits[index] for index in sorted(indexes_used)]

a = TypeVar("a", bound=Hashable)

class Plan(Generic[a]):

    label:str = "objects"
    '''
    Plural string labeling this Plan's object.
    '''

    def __init__(self, versions:list[Version.Version], all_dataminer_collections:list[DataMinerCollection.DataMinerCollection], version_objects:dict[Version.Version,set[a]]) -> None:
        '''
        :versions: The Versions which support all of the same objects.
        :all_dataminer_collections: A list of every DataMinerCollection.
        :version_objects: Dictionary mapping Versions to a set of this Plan's objects supported by that Version.
        '''
        self.versions = versions
        self.items_to_test:list[a] = []

    def add_item(self, item:a) -> None:
        '''
        Adds an item that should be tested when `test` is called.
        Only some items need to be tested; this function determines which.
        Other items can be tested by different Plans.
        :item: The item to add.
        '''
        self.items_to_test.append(item)

    def test(self, all_dataminer_collections:dict[str,DataMinerCollection.DataMinerCollection]) -> list[a]:
        '''
        Tests all items in the `items_to_test` list.
        :all_dataminer_collections: A dictionary of DataMinerCollection names to DataMinerCollections.
        '''
        ...

    @classmethod
    def get_obj(cls, dataminer_collection:DataMinerCollection.DataMinerCollection, version:Version.Version) -> a:
        '''
        Gets this Plan's object from a DataMinerCollection and Version.
        :dataminer_collection: The DataMinerCollection associated with the object.
        :version: The Version associated with the object.
        '''
        ...

    @classmethod
    def sort(cls, item:a) -> "SupportsRichComparison":
        '''
        Returns an object that supports rich comparison from the item.
        '''
        ...

    @classmethod
    def get_name(cls, item:a) -> str:
        '''
        Returns a string representing the object. By default, uses `repr`.
        '''
        return repr(item)

    def __repr__(self) -> str:
        return "<%s [%s]>" % (self.__class__.__name__, ", ".join(version.name for version in self.versions))

def create_test_function(plan_type:type[Plan[a]]) -> Callable[[],None]:
    return lambda: test(plan_type)

def test(plan_type:type[Plan[a]]) -> None:
    versions = Importer.versions
    dataminer_collections = list(Importer.dataminer_collections.values())
    version_objects:dict[Version.Version,set[a]] = {}
    all_objects_set:set[a] = set()
    for version in versions.values():
        version_objects[version] = set()
        for dataminer_collection in dataminer_collections:
            if dataminer_collection.supports_version(version):
                object = plan_type.get_obj(dataminer_collection, version)
                version_objects[version].add(object)
                all_objects_set.add(object)
    all_objects = sorted(all_objects_set, key=plan_type.sort)

    versions_bitboard:dict[Version.Version,int] = {
        version: sum(
            1 << index if object in version_objects[version] else 0
            for index, object in enumerate(all_objects)
        )
        for version in versions.values()
        if len(version_objects[version]) > 0
    }
    unique_versions:defaultdict[int,list[Version.Version]] = defaultdict(lambda: [])
    for version, bits in versions_bitboard.items():
        unique_versions[bits].append(version)

    plans:dict[int, Plan] = {
        bits: plan_type(versions, dataminer_collections, version_objects)
        for bits, versions in unique_versions.items()
    }
    all_bits = list(unique_versions.keys())
    bits_needed = get_overlapping_bits(all_bits, len(all_objects))
    print("Created a plan using %i Versions." % (len(bits_needed),))

    for index, structure in enumerate(all_objects):
        for bits in bits_needed:
            if bits & (1 << index) != 0: # if the version(s) associated with these bits supports this object.
                plans[bits].add_item(structure)
                break
        else:
            assert False, "no plan supports %r" % (structure,)
    failed_objects:list[a] = []
    for bits in bits_needed:
        failed_objects.extend(plans[bits].test({dataminer_collection.name: dataminer_collection for dataminer_collection in dataminer_collections}))
    print("%i %s failed: [%s]" % (len(failed_objects), plan_type.label, ", ".join(plan_type.get_name(object) for object in failed_objects)))
