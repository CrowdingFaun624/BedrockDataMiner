import datetime
import json
import requests

import Utilities.FileManager as FileManager
import Version.Version as Version

def log(version:Version.Version, response:requests.Response, response_length:int) -> None:
    with open(FileManager.DOWNLOAD_LOG, "at") as f:
        f.write(json.dumps({"version": version.name, "time": datetime.datetime.now().isoformat(), "status_code": response.status_code, "headers": {key: value for key, value in response.headers.items()}, "url": response.url, "reason": response.reason, "elapsed": str(response.elapsed), "actual_response_length": response_length}) + "\n")
        
