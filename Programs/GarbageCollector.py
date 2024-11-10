from typing import Callable

import Component.Importer as Importer
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager


def garbage_collect() -> set[int]:
    '''
    Collects every file referenced by anything, returns a list of unused hashes.
    '''
    dataminer_collections = Importer.dataminer_collections
    structure_tags = Importer.structure_tags
    versions = Importer.versions
    referenced_files:set[int] = set()
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

def clean_index() -> None:
    FileStorageManager.remove_index_values_without_associated_file()

def print_all() -> None:
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
    unused_hashes = garbage_collect()
    string_hashes = sorted(File.hash_int_to_str(unused_hash) for unused_hash in unused_hashes)
    print("\n".join(string_hashes))

def remove() -> None:
    unused_hashes = garbage_collect()
    print_stats(unused_hashes)
    while True:
        if input("Are you sure you want to continue? (y/ctrl+C): ") == "y":
            break
    for unused_hash in (File.hash_int_to_str(unused_hash) for unused_hash in unused_hashes):
        FileStorageManager.delete_item(unused_hash)
    FileStorageManager.save_index()
    FileStorageManager.remove_index_values_without_associated_file()

def print_stats(unused_hashes:set[int]|None=None) -> None:
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
        unused_hashes = garbage_collect()
    unused_storage_bytes = sum(FileStorageManager.get_file_path(File.hash_int_to_str(unused_hash)).stat().st_size for unused_hash in unused_hashes)
    print("Found %i unused files (%.2f%% of total) worth %i bytes (%.2f%% of total)." % (len(unused_hashes), 100*len(unused_hashes)/file_count, unused_storage_bytes, 100*unused_storage_bytes/total_storage_bytes))

def main() -> None:
    functions:dict[str,Callable[[],None]] = {
        "clean_index": clean_index,
        "print_all": print_all,
        "remove": remove,
        "stats": print_stats,
    }
    user_input = None
    while user_input not in functions:
        user_input = input("Choose an action from [%s]: " % (", ".join(functions)))
    functions[user_input]()
