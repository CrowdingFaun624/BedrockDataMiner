# import cProfile
# from pathlib2 import Path
# import pstats
# profile = cProfile.Profile()
# profile.run('''
# import Programs.CompareAll as CompareAll
# import DataMiners.DataMiners as DataMiners
# import Programs.AllVersions as AllVersions
# import Version.VersionParser as VersionParser
# import Programs.UrlValidator as UrlValidator
# import Programs.WikiValidator as WikiValidator
# import Programs.Cleaner as Cleaner
# import Programs.FileSummary as FileSummary
# import Programs.GetFile as GetFile
# import Utilities.CustomJson as CustomJson
# import Utilities.FileManager as FileManager
# import Utilities.Nbt.NbtReader as NbtReader
# import Utilities.Scripts as Scripts
# import Utilities.StoredVersionsManager as StoredVersionsManager
# ''')
# with open(Path("./time_report.txt"), "wt") as stream:
#     stats = pstats.Stats(profile, stream=stream)
#     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

import Programs.CompareAll as CompareAll
import DataMiners.DataMiners as DataMiners
import Programs.AllVersions as AllVersions
import Version.VersionParser as VersionParser
import Programs.UrlValidator as UrlValidator
import Programs.WikiValidator as WikiValidator
import Programs.Cleaner as Cleaner
import Programs.FileSummary as FileSummary
import Programs.GetFile as GetFile
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Scripts as Scripts
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
    "Scripts": Scripts.main,
    "StoredVersions": StoredVersionsManager.main,
    "TestStructures": DataMiners.test_structures,
    "UrlValidator": UrlValidator.main,
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
    #     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

    FileManager.clear_temp()

pass
# TODO: dataminers for:
#   renderer/vanilla_lights.json in 1.20.20.23
# TODO: fix meta-dataminers relating to the usage of sound events (use all available sources)
# TODO: merge dict and list structures
# TODO: make more domains
