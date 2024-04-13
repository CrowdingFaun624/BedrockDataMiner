import os

if __name__ == "__main__":
    os.path.split(os.path.split(__file__)[0])

# import cProfile
# from pathlib2 import Path
# import pstats
# profile = cProfile.Profile()
# profile.run('''
# import Programs.CompareAll as CompareAll
# import DataMiners.DataMiners as DataMiners
# import Downloader.AllVersions as AllVersions
# import Downloader.VersionsParser as VersionsParser
# import Downloader.WikiValidator as WikiValidator
# import Programs.Cleaner as Cleaner
# import Programs.FileSummary as FileSummary
# import Programs.GetFile as GetFile
# import Utilities.CustomJson as CustomJson
# import Utilities.FileManager as FileManager
# import Utilities.Nbt.NbtReader as NbtReader
# import Utilities.StoredVersionsManager as StoredVersionsManager''')
# with open(Path("./time_report.txt"), "wt") as stream:
#     stats = pstats.Stats(profile, stream=stream)
#     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

import Programs.CompareAll as CompareAll
import DataMiners.DataMiners as DataMiners
import Downloader.AllVersions as AllVersions
import Downloader.VersionsParser as VersionsParser
import Downloader.WikiValidator as WikiValidator
import Programs.Cleaner as Cleaner
import Programs.FileSummary as FileSummary
import Programs.GetFile as GetFile
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.StoredVersionsManager as StoredVersionsManager

PROGRAM_NAMES = {
    "AllVersions": AllVersions.main,
    "Cleaner": Cleaner.main,
    "CompareAll": CompareAll.main,
    "CustomJson": CustomJson.main,
    "DataMiners": DataMiners.user_interface,
    "FileSummary": FileSummary.main,
    "GetFile": GetFile.main,
    "NbtReader": NbtReader.main,
    "StoredVersions": StoredVersionsManager.main,
    "TestStructures": DataMiners.test_structures,
    "VersionsParser": VersionsParser.main,
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
    #     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

    FileManager.clear_temp()

pass
# TODO: fix meta-dataminers relating to the usage of sound events (use all available sources)
# TODO: make more dataminers
# TODO: make more domains
