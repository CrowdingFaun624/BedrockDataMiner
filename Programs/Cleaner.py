from itertools import product
from pathlib import Path
from typing import Iterable

import Component.Importer as Importer
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import Utilities.UserInput as UserInput
import Version.Version as Version


def __remove_files(files:Iterable[Path]) -> None:
    for file in files:
        file.unlink()

def get_files(versions:list[Version.Version], dataminer_collections:list[AbstractDataMinerCollection.AbstractDataMinerCollection]) -> list[Path]:
    return [
        path
        for version, dataminer_collection in product(versions, dataminer_collections)
        if (path := version.get_version_directory().joinpath("data", dataminer_collection.file_name)).exists()]

def main() -> None:
    versions = UserInput.input_multi(Importer.versions, "version", allow_select_all=True)
    selectable_dataminer_collections = {
        dataminer_collection.name: dataminer_collection
        for dataminer_collection in Importer.dataminer_collections.values()
        if any(dataminer_collection.supports_version(version) for version in versions)
    }
    dataminers = UserInput.input_multi(selectable_dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True)
    files = get_files(versions, dataminers)
    if len(dataminers) == len(Importer.dataminer_collections):
        prompt = "I wish to remove %i versions of EVERY FILE" % (len(files),)
        prompt_input = input("This action will remove %i copies of EVERY FILE. If you wish to continue, type \"%s\": " % (len(files), prompt))
    else:
        prompt = "I wish to remove %i versions of %s" % (len(files), ", ".join(dataminer.name for dataminer in dataminers))
        prompt_input = input("This action will remove %i copies of %s. If you wish to continue, type \"%s\": " % (len(files), ", ".join("\"%s\"" % (dataminer.name,) for dataminer in dataminers), prompt))
    if prompt_input == prompt:
        __remove_files(files)
        print("Successfully removed %i files." % len(files))
    else:
        print("Failed to copy prompt; no files removed.")
