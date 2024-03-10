from pathlib2 import Path
from typing import Iterable

import DataMiners.DataMiners as DataMiners
import Downloader.VersionsParser as VersionsParser

def __remove_files(files:Iterable[Path]) -> None:
    for file in files:
        file.unlink()

def main() -> None:
    version_selected_str = None
    versions_dict = VersionsParser.versions_dict.get()
    while version_selected_str != "*" and version_selected_str not in versions_dict:
        version_selected_str = input("Select a version to remove data from (or \"*\" for all): ")
    if version_selected_str == "*":
        versions_selected = VersionsParser.versions.get()
    else:
        versions_selected = [versions_dict[version_selected_str]]

    dataminer_file_names = [dataminer_collection.file_name for dataminer_collection in DataMiners.dataminers]
    dataminer_selected = None
    while dataminer_selected not in dataminer_file_names:
        dataminer_selected = input("Select a file to clear from %i versions (%s): " % (len(versions_selected), dataminer_file_names))

    files = [path for version in versions_selected if version.version_folder is not None and (path := Path(version.version_folder.joinpath("data", dataminer_selected))).exists()]
    prompt = "I wish to remove %i versions of %s" % (len(files), dataminer_selected)
    prompt_input = input("This action will remove %i copies of \"%s\". If you wish to continue, type \"%s\": " % (len(files), dataminer_selected, prompt))
    if prompt_input == prompt:
        __remove_files(files)
        print("Successfully removed %i files." % len(files))
    else:
        print("Failed to copy prompt; no files removed.")
