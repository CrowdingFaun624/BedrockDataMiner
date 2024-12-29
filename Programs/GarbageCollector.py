from typing import Callable

import Domain.Domain as Domain
import Domain.Domains as Domains
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager
import Utilities.UserInput as UserInput


def garbage_collect(domains:list[Domain.Domain]) -> set[int]:
    '''
    Collects every file referenced by anything, returns a list of unused hashes.
    '''
    referenced_files:set[int] = set()
    for domain in domains:
        dataminer_collections = domain.dataminer_collections
        structure_tags = domain.structure_tags
        versions = domain.versions
        for version in versions.values():
            print(version.name)
            for dataminer_collection in dataminer_collections.values():
                referenced_files.update(dataminer_collection.get_referenced_files(version, structure_tags))
                dataminer_collection.clear_some_caches()
        for dataminer_collection in dataminer_collections.values():
            dataminer_collection.clear_caches()
    existing_files:set[int] = set()
    for folder in FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.iterdir():
        for file in folder.iterdir():
            existing_files.add(File.hash_str_to_int(file.name))
    unused_files = existing_files - referenced_files
    return unused_files

def clean_index(domains:list[Domain.Domain]) -> None:
    FileStorageManager.remove_index_values_without_associated_file()

def print_all(domains:list[Domain.Domain]) -> None:
    file_count = sum(
        1
        for folder in FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.iterdir()
        for file in folder.iterdir()
    )
    total_storage_bytes = sum(
        file.stat().st_size
        for folder in FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.iterdir()
        for file in folder.iterdir()
    )
    unused_hashes = garbage_collect(domains)
    string_hashes = sorted(File.hash_int_to_str(unused_hash) for unused_hash in unused_hashes)
    print("\n".join(string_hashes))

def remove(domains:list[Domain.Domain]) -> None:
    unused_hashes = garbage_collect(domains)
    print_stats(domains, unused_hashes)
    while True:
        if input("Are you sure you want to continue? (y/ctrl+C): ") == "y":
            break
    for unused_hash in (File.hash_int_to_str(unused_hash) for unused_hash in unused_hashes):
        FileStorageManager.delete_item(unused_hash)
    FileStorageManager.index.write()
    FileStorageManager.remove_index_values_without_associated_file()

def print_stats(domains:list[Domain.Domain], unused_hashes:set[int]|None=None) -> None:
    file_count = sum(
        1
        for folder in FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.iterdir()
        for file in folder.iterdir()
    )
    total_storage_bytes = sum(
        file.stat().st_size
        for folder in FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.iterdir()
        for file in folder.iterdir()
    )
    if unused_hashes is None:
        unused_hashes = garbage_collect(domains)
    unused_storage_bytes = sum(FileStorageManager.get_file_path(File.hash_int_to_str(unused_hash)).stat().st_size for unused_hash in unused_hashes)
    print(f"Found {len(unused_hashes)} unused files ({100*len(unused_hashes)/file_count:.2f}% of total) worth {unused_storage_bytes} bytes ({100*unused_storage_bytes/total_storage_bytes:.2f}% of total).")

def main(domain:Domain.Domain) -> None:
    functions:dict[str,Callable[[list[Domain.Domain]],None]] = {
        "clean_index": clean_index,
        "print_all": print_all,
        "remove": remove,
        "stats": print_stats,
    }
    domains = list(Domains.domains.values())
    UserInput.input_single(functions, "program", show_options=True, close_enough=True)(domains)
