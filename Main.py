import os

if __name__ == "__main__":
    os.path.split(os.path.split(__file__)[0])

import Utilities.FileManager as FileManager
import Downloader.AllVersions as AllVersions
import Programs.GetFile as GetFile
import Utilities.StoredVersionsManager as StoredVersionsManager
import Downloader.VersionsParser as VersionParser
import Downloader.WikiValidator as WikiValidator

PROGRAM_NAMES = {
    "AllVersions": AllVersions.main,
    "GetFile": GetFile.main,
    "StoredVersions": StoredVersionsManager.main,
    "VersionParser": VersionParser.main,
    "WikiValidator": WikiValidator.main,
}

if __name__ == "__main__":
    user_input = None
    while user_input not in PROGRAM_NAMES:
        user_input = input("Choose a program (%s):\n" % str(list(PROGRAM_NAMES.keys())))
    PROGRAM_NAMES[user_input]()

FileManager.clear_temp()
