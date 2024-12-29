from itertools import product
from pathlib import Path
from typing import Iterable

import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import Domain.Domain as Domain
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

def main(domain:Domain.Domain) -> None:
    versions = UserInput.input_multi(domain.versions, "version", allow_select_all=True)
    selectable_dataminer_collections = {
        dataminer_collection.name: dataminer_collection
        for dataminer_collection in domain.dataminer_collections.values()
        if any(dataminer_collection.supports_version(version) for version in versions)
    }
    dataminers = UserInput.input_multi(selectable_dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True)
    files = get_files(versions, dataminers)
    if len(dataminers) == len(domain.dataminer_collections):
        prompt = f"I wish to remove {len(files)} versions of EVERY FILE"
        prompt_input = input(f"This action will remove {len(files)} copies of EVERY FILE. If you wish to continue, type \"{prompt}\": ")
    else:
        prompt = f"I wish to remove {len(files)} versions of {", ".join(dataminer.name for dataminer in dataminers)}"
        prompt_input = input(f"This action will remove {len(files)} copies of {", ".join(f"\"{dataminer.name}\"" for dataminer in dataminers)}. If you wish to continue, type \"{prompt}\": ")
    if prompt_input == prompt:
        __remove_files(files)
        print(f"Successfully removed {len(files)} files.")
    else:
        print("Failed to copy prompt; no files removed.")
