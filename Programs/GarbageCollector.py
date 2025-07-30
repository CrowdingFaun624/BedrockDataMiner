import gzip
from typing import Callable

import Domain.Domain as Domain
import Utilities.FileStorage as FileStorage
from Domain.Domains import domains
from Utilities.File import hash_int_to_str, hash_str_to_int
from Utilities.FileManager import FILE_STORAGE_OBJECTS_DIRECTORY, OUTPUT_DIRECTORY
from Utilities.MemoryUsage import memory_usage
from Utilities.UserInput import input_single


def garbage_collect(domains:list[Domain.Domain]) -> set[int]:
    '''
    Collects every file referenced by anything, returns a list of unused hashes.
    '''
    referenced_files:set[int] = set()
    for domain in domains:
        domain.import_components()
        print(domain.name)
        dataminer_collections = domain.dataminer_collections
        structure_tags = domain.structure_tags
        versions = list(reversed(list(domain.versions.values())))

        for version in versions:
            print(f"\t{version.name}")
            dataminer_collection = None
            try:
                version.get_referenced_files(referenced_files)
                for dataminer_collection in dataminer_collections.values():
                    # print(f"\t\t{dataminer_collection}")
                    dataminer_collection.get_referenced_files(version, structure_tags, referenced_files)
                    dataminer_collection.clear_old_caches({(version, dataminer_collection.get_structure_info(version))})
                memory_usage.adjust()
            except Exception:
                if dataminer_collection is None:
                    print(f"Failed to get files for Version {version.name}.")
                else:
                    print(f"Failed to get files for Version {version.name} on {dataminer_collection}.")
                raise
            version.close_accessors()
        referenced_files.update(domain.active_file_hashes)

        for dataminer_collection in dataminer_collections.values():
            dataminer_collection.clear_all_caches()
        memory_usage.adjust()

    existing_files:set[int] = set()
    for folder in FILE_STORAGE_OBJECTS_DIRECTORY.iterdir():
        for file in folder.iterdir():
            existing_files.add(hash_str_to_int(file.name))
    memory_usage.reset()
    unused_files = existing_files - referenced_files
    return unused_files

def archive_unused(unused_hashes:set[int]) -> None:
    index:list[str] = []
    index_file = OUTPUT_DIRECTORY.joinpath("index.txt")
    output_directory = OUTPUT_DIRECTORY.joinpath("objects")
    output_directory.mkdir()
    for unused_hash in unused_hashes:
        hash_string = hash_int_to_str(unused_hash)
        if (is_zipped := FileStorage.index.get().get(hash_string)) is None:
            continue
        index.append(f"{hash_string} {int(is_zipped)}")
        directory = output_directory.joinpath(hash_string[:2])
        directory.mkdir(exist_ok=True)
        file_path = directory.joinpath(hash_string)
        with open(file_path, "wb") as destination:
            data = FileStorage.read_archived(hash_string)
            if is_zipped:
                destination.write(gzip.compress(data))
            else:
                destination.write(data)
    with open(index_file, "wt") as f:
        f.write("\n".join(index))

def clean_index(unused_hashes:set[int]) -> None:
    FileStorage.remove_index_values_without_associated_file()

def print_all(unused_hashes:set[int]) -> None:
    string_hashes = sorted(hash_int_to_str(unused_hash) for unused_hash in unused_hashes)
    print("\n".join(string_hashes))

def remove(unused_hashes:set[int]) -> None:
    while True:
        if input("Are you sure you want to continue? (y/ctrl+C): ") == "y":
            break
    FileStorage.recycle_items(hash_int_to_str(unused_hash) for unused_hash in unused_hashes)
    FileStorage.remove_index_values_without_associated_file()

def print_stats(unused_hashes:set[int]) -> None:
    file_count = sum(
        1
        for folder in FILE_STORAGE_OBJECTS_DIRECTORY.iterdir()
        for file in folder.iterdir()
    )
    total_storage_bytes = sum(
        file.stat().st_size
        for folder in FILE_STORAGE_OBJECTS_DIRECTORY.iterdir()
        for file in folder.iterdir()
    )
    unused_storage_bytes = sum(FileStorage.get_file_path(hash_int_to_str(unused_hash)).stat().st_size for unused_hash in unused_hashes)
    print(f"Found {len(unused_hashes)} unused files ({100*len(unused_hashes)/file_count:.2f}% of total) worth {unused_storage_bytes} bytes ({100*unused_storage_bytes/total_storage_bytes:.2f}% of total).")

def main(domain:Domain.Domain) -> None:
    domains_list = list(domains.values())
    domains_list.remove(domain)
    domains_list.insert(0, domain) # put selected Domain first.
    unused_files:set[int] = garbage_collect(domains_list)
    exit_now = [False]
    functions:dict[str,Callable[[set[int]],None]] = {
        "archive_unused": archive_unused,
        "clean_index": clean_index,
        "exit": lambda unused_hashes: exit_now.__setitem__(0, True),
        "print_all": print_all,
        "remove": remove,
        "stats": print_stats,
    }
    while not exit_now[0]:
        input_single(functions, "program", show_options=True, close_enough=True)(unused_files)
