from datetime import datetime
from typing import TYPE_CHECKING, Any, BinaryIO, TypedDict

from Downloader.Accessor import Accessor
from Downloader.FileAccessor import FileAccessor
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

if TYPE_CHECKING:
    import requests

class InstanceArgumentsTypedDict(TypedDict):
    url: str

class PropagatedArgumentsTypedDict(TypedDict):
    location: str

class DownloadAccessor(FileAccessor):

    propagated_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, str),
    )
    
    instance_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("url", True, str),
    )

    __slots__ = (
        "_installed",
        "file_handle",
        "location",
        "url",
    )

    def prepare_for_install(self, instance_arguments:InstanceArgumentsTypedDict, class_arguments:dict[str,Any], propagated_arguments:PropagatedArgumentsTypedDict, linked_accessors:dict[str,Accessor]) -> None:
        version_directory = self.version.version_directory
        location = version_directory.joinpath(propagated_arguments["location"])
        self.location = location
        self._installed:bool|None = None
        self.file_handle:BinaryIO|None = None

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
                "time": datetime.now().isoformat(),
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
        if self.file_handle is None:
            self.file_handle = open(self.location, "rb")
        return self.file_handle

    def close(self) -> None:
        super().close()
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

    def install(self) -> None:
        if not self.installed:
            import requests
            with open(self.location, "wb") as f, requests.get(self.url) as response:
                f.write(self.log(response).content)
            self._installed = True

    def all_done(self) -> None:
        super().all_done()
        self._installed = False
        if self.file_handle is not None:
            self.file_handle.close()
        if self.location.exists():
            self.location.unlink()
