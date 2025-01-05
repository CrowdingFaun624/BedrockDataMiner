import datetime
from typing import TYPE_CHECKING, Any, BinaryIO, TypedDict

import Downloader.Accessor as Accessor
import Downloader.FileAccessor as FileAccessor
import Utilities.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import requests

class InstanceArgumentsTypedDict(TypedDict):
    url: str

class PropagatedArgumentsTypedDict(TypedDict):
    location: str

class DownloadAccessor(FileAccessor.FileAccessor):

    propagated_parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )
    
    instance_parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("url", "a str", True, str),
    )

    def prepare_for_install(self, instance_arguments:InstanceArgumentsTypedDict, class_arguments:dict[str,Any], propagated_arguments:PropagatedArgumentsTypedDict, linked_accessors:dict[str,Accessor.Accessor]) -> None:
        version_directory = self.version.version_directory
        location = version_directory.joinpath(propagated_arguments["location"])
        self.location = location
        self._installed:bool|None = None

        self.url = instance_arguments["url"]

    @property
    def installed(self) -> bool:
        if self._installed is None:
            self._installed = self.location.exists()
        return self._installed

    def log(self, response:"requests.Response") -> "requests.Response":
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
            import requests
            with open(self.location, "wb") as f, requests.get(self.url) as response:
                f.write(self.log(response).content)
            self._installed = True

    def all_done(self) -> None:
        self._installed = False
        if self.location.exists():
            self.location.unlink()
