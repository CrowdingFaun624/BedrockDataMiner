# import cProfile
# import pstats

# from pathlib2 import Path

# profile = cProfile.Profile()
# profile.run('''
# import DataMiner.DataMiners as DataMiners
# import Programs.AllVersions as AllVersions
# import Programs.Cleaner as Cleaner
# import Programs.CompareAll as CompareAll
# import Programs.Coverage as Coverage
# import Programs.FileSummary as FileSummary
# import Programs.GetFile as GetFile
# import Programs.Test.Tests as Tests
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

PROGRAM_NAMES = ["AllVersions", "Cleaner", "CompareAll", "Coverage", "CustomJson", "DataMiners", "FileSummary", "GarbageCollector", "GetFile", "NbtReader", "Scripts", "StoredVersions", "Tablifiers", "Tests", "UrlValidator"]

user_input_lock = threading.Lock()

def get_user_input() -> None:
    with user_input_lock:
        output = ""
        while output not in PROGRAM_NAMES:
            try:
                output = input("Choose a program (%s):\n" % (PROGRAM_NAMES))
            except EOFError:
                exit()
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
import Programs.Coverage as Coverage
import Programs.FileSummary as FileSummary
import Programs.GarbageCollector as GarbageCollector
import Programs.GetFile as GetFile
import Programs.Test.Tests as Tests
import Programs.UrlValidator as UrlValidator
import Tablifier.Tablifiers as Tablifiers
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Scripts as Scripts
import Utilities.StoredVersionsManager as StoredVersionsManager

with open(FileManager.STRUCTURE_LOG_FILE, "wt") as f:
    f.write("")

PROGRAM_FUNCTIONS:dict[str,Callable[[],None]] = {
    "AllVersions": AllVersions.main,
    "Cleaner": Cleaner.main,
    "CompareAll": CompareAll.main,
    "Coverage": Coverage.main,
    "CustomJson": CustomJson.main,
    "DataMiners": DataMiners.user_interface,
    "FileSummary": FileSummary.main,
    "GarbageCollector": GarbageCollector.main,
    "GetFile": GetFile.main,
    "NbtReader": NbtReader.main,
    "Scripts": Scripts.main,
    "StoredVersions": StoredVersionsManager.main,
    "Tablifiers": Tablifiers.main,
    "Tests": Tests.main,
    "UrlValidator": UrlValidator.main,
}

def main() -> None:
    with user_input_lock:
        if user_input[0] is not None:
            # import pprofile
            # profile = pprofile.Profile()
            # with profile():
            #     PROGRAM_FUNCTIONS[user_input[0]]()
            # profile.dump_stats("./time_report.txt")

            # import cProfile
            # from pathlib2 import Path
            # import pstats
            # profile = cProfile.Profile()
            # profile.run("PROGRAM_FUNCTIONS[user_input[0]]()")
            # with open(Path("./time_report.txt"), "wt") as stream:
            #     stats = pstats.Stats(profile, stream=stream)
            #     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

            PROGRAM_FUNCTIONS[user_input[0]]()
    FileManager.clear_temp()

if __name__ == "__main__":
    main()

pass
# TODO: make logging of errors slightly better.
# TODO: create a DynamicGroupStructure class that uses a function to decide which branch to use instead of the type of the data.

# TODO: make more domains
# TODO: make comparisons out of HTML and fancy and collapsible and stuff.
