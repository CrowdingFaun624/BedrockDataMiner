# import cProfile
# import pstats

# from pathlib2 import Path

# profile = cProfile.Profile()
# profile.run('''
# import DataMiner.DataMiners as DataMiners
# import Programs.AllVersions as AllVersions
# import Programs.Cleaner as Cleaner
# import Programs.CompareAll as CompareAll
# import Programs.FileSummary as FileSummary
# import Programs.GetFile as GetFile
# import Programs.UrlValidator as UrlValidator
# import Utilities.CustomJson as CustomJson
# import Utilities.FileManager as FileManager
# import Utilities.Nbt.NbtReader as NbtReader
# import Utilities.Scripts as Scripts
# import Utilities.StoredVersionsManager as StoredVersionsManager
# ''')
# with open(Path("./time_report.txt"), "wt") as stream:
#     stats = pstats.Stats(profile, stream=stream)
#     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

import threading
from typing import Any, Callable

PROGRAM_NAMES = ["AllVersions", "Cleaner", "CompareAll", "CustomJson", "DataMiners", "FileSummary", "GetFile", "NbtReader", "Scripts", "StoredVersions", "TestStructures", "UrlValidator", "WikiValidator"]

user_input_lock = threading.Lock()

def get_user_input() -> None:
    with user_input_lock:
        output = ""
        while output not in PROGRAM_NAMES:
            output = input("Choose a program (%s):\n" % (PROGRAM_NAMES))
        user_input[0] = output
user_input:list[Any] = [None]
if __name__ == "__main__":
    import threading
    user_thread = threading.Thread(target=get_user_input, daemon=True)
    user_thread.start()

import DataMiner.DataMiners as DataMiners
import Programs.AllVersions as AllVersions
import Programs.Cleaner as Cleaner
import Programs.CompareAll as CompareAll
import Programs.FileSummary as FileSummary
import Programs.GetFile as GetFile
import Programs.UrlValidator as UrlValidator
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Scripts as Scripts
import Utilities.StoredVersionsManager as StoredVersionsManager

PROGRAM_FUNCTIONS:dict[str,Callable[[],None]] = {
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
}

def main() -> None:
    with user_input_lock:
        if user_input[0] is not None:
            PROGRAM_FUNCTIONS[user_input[0]]()

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
# TODO: utilize https://archive.org/details/minecraft-iOS to fill in missing versions
# TODO: dataminers for:
#   renderer/vanilla_lights.json in 1.20.20.23
# TODO: fix meta-dataminers relating to the usage of sound events (use all available sources)
# TODO: merge dict and list structures
# TODO: make more domains
