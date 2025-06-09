# import cProfile
# import pstats
# from pathlib import Path

# profile = cProfile.Profile()
# profile.run('''
# import Domain.Domains as Domains
# Domains.domains["minecraft_java"].import_components()
# ''')
# with open(Path("./time_report.txt"), "wt") as stream:
#     stats = pstats.Stats(profile, stream=stream)
#     stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

# import pprofile

import threading
from typing import Any, Callable

import Domain.Domains as Domains

# profile = pprofile.Profile()
# with profile():
#     import Domain.Domains as Domains
#     Domains.domains["minecraft_bedrock"].import_components()
# profile.dump_stats("./time_report.txt")

PROGRAM_NAMES = ("AllVersions", "Cleaner", "CompareAll", "CompareSome", "Dataminers", "FileStorage", "GarbageCollector", "Scripts", "SimilarityTester", "Tablifiers", "Tests")

lock1 = threading.Lock() # domain input
lock2 = threading.Lock() # program input

def get_user_input() -> None:
    import Utilities.UserInput as UserInput
    with lock2:
        with lock1:
            aliases = {domain_name: domain.aliases for domain_name, domain in Domains.domains.items() if not domain.is_library}
            domains = {domain_name: domain for domain_name, domain in Domains.domains.items() if not domain.is_library}
            user_input[0] = UserInput.input_single(domains, "domain", show_options=True, close_enough=True, close_enough_threshold=5, enter_can_pick_only=True, aliases=aliases, behavior_on_eof=exit)
        user_input[1] = UserInput.input_single({name: name for name in PROGRAM_NAMES}, "program", show_options=True, close_enough=True, behavior_on_eof=exit)

user_input:list[Any] = [None, None]
if __name__ == "__main__":
    import threading
    user_thread = threading.Thread(target=get_user_input, daemon=True)
    user_thread.start()

import Dataminer.Dataminers as Dataminers
import Domain.Domain as Domain
import Programs.AllVersions as AllVersions
import Programs.Cleaner as Cleaner
import Programs.CompareAll as CompareAll
import Programs.GarbageCollector as GarbageCollector
import Programs.SimilarityTester as SimilarityTester
import Programs.Test.Tests as Tests
import Tablifier.Tablifiers as Tablifiers
import Utilities.FileManager as FileManager
import Utilities.FileStorage as FileStorage
import Utilities.Scripts as Scripts

PROGRAM_FUNCTIONS:dict[str,Callable[[Domain.Domain],None]] = {
    "AllVersions": AllVersions.main,
    "Cleaner": Cleaner.main,
    "CompareAll": CompareAll.main,
    "CompareSome": CompareAll.compare_some,
    "Dataminers": Dataminers.user_interface,
    "FileStorage": FileStorage.main,
    "GarbageCollector": GarbageCollector.main,
    "Scripts": Scripts.main,
    "SimilarityTester": SimilarityTester.main,
    "Tablifiers": Tablifiers.main,
    "Tests": Tests.main,
}

def main() -> None:
    with lock1:
        domain:"Domain.Domain" = user_input[0]
    if domain is not None:
        domain.import_components()
        with lock2:
            if user_input[1] is not None:
                PROGRAM_FUNCTIONS[user_input[1]](domain)
    FileManager.clear_temp()

if __name__ == "__main__":
    main()
