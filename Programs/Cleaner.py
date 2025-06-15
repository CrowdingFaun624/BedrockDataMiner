import datetime
import shutil
from itertools import product
from pathlib import Path
from typing import Iterable

from send2trash import send2trash

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Utilities.FileManager import OUTPUT_DIRECTORY, get_temp_file_path
from Utilities.UserInput import input_multi
from Version.Version import Version


def recycle_files(files:Iterable[Path], domain:"Domain.Domain") -> None:
    versions_directory = domain.versions_directory
    temp_directory = get_temp_file_path()
    temp_directory.mkdir()
    for source_path in files:
        destination_path = temp_directory.joinpath(source_path.relative_to(versions_directory))
        for item in reversed(destination_path.relative_to(temp_directory).parents):
            temp_directory.joinpath(item).mkdir(exist_ok=True)
        shutil.move(source_path, destination_path)
    output_recycle_directory = OUTPUT_DIRECTORY.joinpath(f"recycled-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}")
    shutil.move(temp_directory, output_recycle_directory)
    send2trash(output_recycle_directory)

def get_files(versions:list[Version], dataminer_collections:list[AbstractDataminerCollection]) -> list[Path]:
    return [
        path
        for version, dataminer_collection in product(versions, dataminer_collections)
        if (path := version.version_directory.joinpath("data", dataminer_collection.file_name)).exists()
    ]

def main(domain:Domain.Domain) -> None:
    versions = input_multi(domain.versions, "version", allow_select_all=True)
    selectable_dataminer_collections = {
        dataminer_collection.name: dataminer_collection
        for dataminer_collection in domain.dataminer_collections.values()
        if any(dataminer_collection.supports_version(version) for version in versions)
    }
    dataminers = input_multi(selectable_dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True)
    files = get_files(versions, dataminers)
    recycle_files(files, domain)
    print(f"Successfully removed {len(files)} files.")
