import os

if __name__ == "__main__":
    os.path.split(os.path.split(__file__)[0])

import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager as StoredVersionsManager
import Downloader.VersionsParser as VersionParser

PROGRAM_NAMES = {
    "StoredVersions": StoredVersionsManager.main,
    "VersionParser": VersionParser.main,
}

if __name__ == "__main__":
    user_input = None
    while user_input not in PROGRAM_NAMES:
        user_input = input("Choose a program (%s):\n" % str(list(PROGRAM_NAMES.keys())))
    PROGRAM_NAMES[user_input]()