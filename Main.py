# import cProfile
# import pstats

# from pathlib import Path

# profile = cProfile.Profile()
# profile.run('''
# import DataMiner.DataMiners as DataMiners
# import Programs.AllVersions as AllVersions
# import Programs.Cleaner as Cleaner
# import Programs.CompareAll as CompareAll
# import Programs.Test.Tests as Tests
# import Utilities.FileManager as FileManager
# import Utilities.FileStorageManager as FileStorageManager
# import Utilities.Scripts as Scripts
# ''')
# with open(Path("./time_report.txt"), "wt") as stream:
#     stats = pstats.Stats(profile, stream=stream)
#     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

import threading
from typing import Any, Callable

import Domain.Domains as Domains

PROGRAM_NAMES = ["AllVersions", "Cleaner", "CompareAll", "DataMiners", "FileStorage", "GarbageCollector", "Scripts", "Tablifiers", "Tests"]

user_input_lock = threading.Lock()

def get_user_input() -> None:
    import Utilities.UserInput as UserInput
    with user_input_lock:
        user_input[0] = domain = UserInput.input_single(Domains.domains, "domain", show_options=True, close_enough=True, close_enough_threshold=5, enter_can_pick_only=True)
        try:
            domain.import_components()
        except Exception as e:
            user_input[1] = e
        else:
            user_input[1] = UserInput.input_single({name: name for name in PROGRAM_NAMES}, "program", show_options=True, close_enough=True, behavior_on_eof=exit)

user_input:list[Any] = [None, None]
if __name__ == "__main__":
    import threading
    user_thread = threading.Thread(target=get_user_input, daemon=True)
    user_thread.start()

import DataMiner.DataMiners as DataMiners
import Domain.Domain as Domain
import Programs.AllVersions as AllVersions
import Programs.Cleaner as Cleaner
import Programs.CompareAll as CompareAll
import Programs.GarbageCollector as GarbageCollector
import Programs.Test.Tests as Tests
import Tablifier.Tablifiers as Tablifiers
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager
import Utilities.Scripts as Scripts

PROGRAM_FUNCTIONS:dict[str,Callable[[Domain.Domain],None]] = {
    "AllVersions": AllVersions.main,
    "Cleaner": Cleaner.main,
    "CompareAll": CompareAll.main,
    "DataMiners": DataMiners.user_interface,
    "FileStorage": FileStorageManager.main,
    "GarbageCollector": GarbageCollector.main,
    "Scripts": Scripts.main,
    "Tablifiers": Tablifiers.main,
    "Tests": Tests.main,
}

def main() -> None:
    with user_input_lock:
        if user_input[0] is not None and user_input[1] is not None:
            # import pprofile
            # profile = pprofile.Profile()
            # with profile():
            #     PROGRAM_FUNCTIONS[user_input[0]]()
            # profile.dump_stats("./time_report.txt")

            # import cProfile
            # from pathlib import Path
            # import pstats
            # profile = cProfile.Profile()
            # profile.run("PROGRAM_FUNCTIONS[user_input[0]]()")
            # with open(Path("./time_report.txt"), "wt") as stream:
            #     stats = pstats.Stats(profile, stream=stream)
            #     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
            if isinstance(user_input[1], Exception):
                raise user_input[1]
            PROGRAM_FUNCTIONS[user_input[1]](user_input[0])
    FileManager.clear_temp()

if __name__ == "__main__":
    main()

pass
# TODO: make logging of errors slightly better.
# TODO: Make a module specifically for getting user input.
# TODO: create a DynamicGroupStructure class that uses a function to decide which branch to use instead of the type of the data.

# TODO: make more domains
# TODO: make comparisons out of HTML and fancy and collapsible and stuff.
