from typing import Iterable

from pathlib2 import Path

import Component.Importer as Importer
import DataMiner.DataMiners as DataMiners
import Version.Version as Version


def __remove_files(files:Iterable[Path]) -> None:
    for file in files:
        file.unlink()

def get_files(versions_selected:Iterable[Version.Version], file_name:str) -> list[Path]:
    return [path for version in versions_selected if (path := version.get_version_directory().joinpath("data", file_name)).exists()]

def main() -> None:
    version_selected_str = None
    versions = Importer.versions
    while version_selected_str != "*" and version_selected_str not in versions:
        version_selected_str = input("Select a version to remove data from (or \"*\" for all): ")
    if version_selected_str == "*":
        versions_selected = Importer.versions.values()
    else:
        versions_selected = [versions[version_selected_str]]

    dataminer_file_names = [dataminer_collection.file_name for dataminer_collection in DataMiners.dataminers]
    dataminer_selected = None
    while dataminer_selected not in dataminer_file_names and dataminer_selected != "*":
        dataminer_selected = input("Select a file to clear from %i versions (or \"*\" for all) (%s): " % (len(versions_selected), dataminer_file_names))

    if dataminer_selected == "*":
        files = [file for file_name in dataminer_file_names for file in get_files(versions_selected, file_name)]
    else:
        files = get_files(versions_selected, dataminer_selected)
    if dataminer_selected == "*":
        prompt = "I wish to remove %i versions of EVERY FILE" % (len(files))
        prompt_input = input("This action will remove %i copies of EVERY FILE. If you wish to continue, type \"%s\": " % (len(files), prompt))
    else:
        prompt = "I wish to remove %i versions of %s" % (len(files), dataminer_selected)
        prompt_input = input("This action will remove %i copies of \"%s\". If you wish to continue, type \"%s\": " % (len(files), dataminer_selected, prompt))
    if prompt_input == prompt:
        __remove_files(files)
        print("Successfully removed %i files." % len(files))
    else:
        print("Failed to copy prompt; no files removed.")
