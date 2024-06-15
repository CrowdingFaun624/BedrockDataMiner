from typing import Any

import Downloader.Manager as Manager


class DummyManager(Manager.Manager):
    "Manager that does nothing. Will raise an exception if a method is accessed."
    
    def prepare_for_install(self, vfile_type_parameters: dict[str, Any]) -> None:
        pass
