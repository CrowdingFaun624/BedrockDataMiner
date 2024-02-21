import os

if __name__ == "__main__":
    os.path.split(os.path.split(__file__)[0])

# import cProfile
# from pathlib2 import Path
# import pstats
# profile = cProfile.Profile()
# profile.run('''
# import Comparison.CompareAll as CompareAll
# import DataMiners.DataMiners as DataMiners
# import Downloader.AllVersions as AllVersions
# import Downloader.VersionsParser as VersionsParser
# import Downloader.WikiValidator as WikiValidator
# import Programs.Cleaner as Cleaner
# import Programs.FileSummary as FileSummary
# import Programs.GetFile as GetFile
# import Utilities.FileManager as FileManager
# import Utilities.StoredVersionsManager as StoredVersionsManager''')
# with open(Path("./time_report.txt"), "wt") as stream:
#     stats = pstats.Stats(profile, stream=stream)
#     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

import Comparison.CompareAll as CompareAll
import DataMiners.DataMiners as DataMiners
import Downloader.AllVersions as AllVersions
import Downloader.VersionsParser as VersionsParser
import Downloader.WikiValidator as WikiValidator
import Programs.Cleaner as Cleaner
import Programs.FileSummary as FileSummary
import Programs.GetFile as GetFile
import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager as StoredVersionsManager

PROGRAM_NAMES = {
    "AllVersions": AllVersions.main,
    "Cleaner": Cleaner.main,
    "CompareAll": CompareAll.main,
    "DataMiners": DataMiners.user_interface,
    "FileSummary": FileSummary.main,
    "GetFile": GetFile.main,
    "StoredVersions": StoredVersionsManager.main,
    "TestComparers": DataMiners.test_comparers,
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
# TODO: remove normalizer_dependencies from where it doesn't belong.
# TODO: remove key_types; change value_types to types in comparer jsons
# TODO: add special key for Comparers that makes it check types (for debugging)
# TODO: rewrite comparer documentation
# TODO: make more dataminers
# TODO: make more domains
