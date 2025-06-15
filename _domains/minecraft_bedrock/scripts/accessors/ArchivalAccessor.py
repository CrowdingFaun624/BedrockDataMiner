from pathlib import Path
from typing import Any, BinaryIO, cast

import Domain.Domain as Domain
from Downloader.Accessor import Accessor
from Downloader.FileAccessor import FileAccessor
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier
from Version.Version import Version


class ArchivalAccessor(FileAccessor):

    __slots__ = (
        "archive_directory",
        "archive_location",
        "source_accessor",
    )

    linked_accessor_types = {"source": FileAccessor}

    class_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("archive_location", True, str),
    )

    def __init__(self, full_name: str, version: Version, domain: Domain.Domain, instance_arguments: dict[str, Any], class_arguments: dict[str, Any], propagated_arguments: dict[str, Any], linked_accessors: dict[str, Accessor]) -> None:
        super().__init__(full_name, version, domain, instance_arguments, class_arguments, propagated_arguments, linked_accessors)
        self.archive_directory = Path(class_arguments["archive_location"]).joinpath(version.name)
        self.archive_location = self.archive_directory.joinpath("client.zip")
        self.source_accessor:FileAccessor = cast(Any, linked_accessors["source"])

    def store(self) -> None:
        if not self.archive_location.exists():
            output = self.source_accessor.read()
            self.archive_directory.mkdir(exist_ok=True)
            with open(self.archive_location, "wb") as f:
                f.write(output)

    def read(self) -> bytes:
        if self.archive_location.exists():
            with open(self.archive_location, "rb") as f:
                return f.read()
        else:
            output = self.source_accessor.read()
            self.archive_directory.mkdir(exist_ok=True)
            with open(self.archive_location, "wb") as f:
                f.write(output)
            return output

    def open(self) -> BinaryIO:
        if not self.archive_location.exists():
            self.store()
        return self.archive_location.open("rb")
