from typing import Any

import Downloader.Manager as Manager
import Version.VersionTags as VersionTags


class DummyManager(Manager.Manager):
    "Manager that does nothing. Will raise an exception if a method is accessed."
    
    def prepare_for_install(self, version_tags: VersionTags.VersionTags, file_type_parameters: dict[str, Any]) -> None:
        pass
