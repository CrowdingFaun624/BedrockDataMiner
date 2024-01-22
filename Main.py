import os

if __name__ == "__main__":
    os.path.split(os.path.split(__file__)[0])

import Utilities.FileManager as FileManager
import DataMiners.DataMiners as DataMiners
import Downloader.AllVersions as AllVersions
import Comparison.CompareAll as CompareAll
import Programs.Cleaner as Cleaner
import Programs.FileSummary as FileSummary
import Programs.GetFile as GetFile
import Utilities.StoredVersionsManager as StoredVersionsManager
import Downloader.VersionsParser as VersionParser
import Downloader.WikiValidator as WikiValidator

PROGRAM_NAMES = {
    "AllVersions": AllVersions.main,
    "Cleaner": Cleaner.main,
    "CompareAll": CompareAll.main,
    "DataMiners": DataMiners.user_interface,
    "FileSummary": FileSummary.main,
    "GetFile": GetFile.main,
    "StoredVersions": StoredVersionsManager.main,
    "VersionParser": VersionParser.main,
    "WikiValidator": WikiValidator.main,
}

def main() -> None:
    user_input = None
    while user_input not in PROGRAM_NAMES:
        user_input = input("Choose a program (%s):\n" % str(list(PROGRAM_NAMES.keys())))
    PROGRAM_NAMES[user_input]()

if __name__ == "__main__":
    main()
    # import cProfile
    # from pathlib2 import Path
    # import pstats
    # profile = cProfile.Profile()
    # profile.run("main()")
    # with open(Path("./time_report.txt"), "wt") as stream:
    #     stats = pstats.Stats(profile, stream=stream)
    #     stats.print_stats()

    FileManager.clear_temp()
