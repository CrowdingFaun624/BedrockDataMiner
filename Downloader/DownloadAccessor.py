import datetime
import time
from typing import BinaryIO, TypedDict

import requests

import Downloader.Accessor as Accessor
import Downloader.FileAccessor as FileAccessor
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class InstanceArgumentsTypedDict(TypedDict):
    url: str

class ClassArgumentsTypedDict(TypedDict):
    location: str

class DownloadAccessor(FileAccessor.FileAccessor):

    class_parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )
    
    instance_parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("url", "a str", True, str),
    )

    def prepare_for_install(self, instance_arguments:InstanceArgumentsTypedDict, class_arguments:ClassArgumentsTypedDict, linked_accessors:dict[str,Accessor.Accessor]) -> None:
        version_directory = self.version.get_version_directory()
        location = version_directory.joinpath(class_arguments["location"])
        if version_directory not in location.parents:
            raise Exceptions.InvalidFileLocationError(location, version_directory)
        self.location = location
        self._installed:bool|None = None

        self.url = instance_arguments["url"]

    @property
    def installed(self) -> bool:
        if self._installed is None:
            self._installed = self.location.exists()
        return self._installed

    def log(self, response:requests.Response) -> requests.Response:
        if (log := self.domain.logs.get("download_log")) is not None and log.supports_type(log, dict):
            log.write({
                "version": self.version.name,
                "time": datetime.datetime.now().isoformat(),
                "status_code": response.status_code,
                "headers": {key: value for key, value in response.headers.items()},
                "url": response.url,
                "reason": response.reason,
                "elapsed": str(response.elapsed),
                "actual_response_length": len(response.content)
            })
        return response

    def open(self) -> BinaryIO:
        self.install()
        return open(self.location, "rb")

    def install(self) -> None:
        if not self.installed:
            response_supposed_length = None
            response_length = 0
            tries = 0
            while response_supposed_length is None or response_supposed_length != response_length:
                with open(self.location, "wb") as f, requests.get(self.url) as response:
                    response_length = len(response.content)
                    response_supposed_length = int(response.headers.get("Content-Length", "0"))
                    f.write(self.log(response).content)
                tries += 1
                if tries >= 5:
                    raise Exceptions.DownloadAccessorFailError(self, self.url)
                if response_supposed_length != response_length:
                    time.sleep(1)
            self._installed = True

    def all_done(self) -> None:
        self._installed = False
        if self.location.exists():
            self.location.unlink()
