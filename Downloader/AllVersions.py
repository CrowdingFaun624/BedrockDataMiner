import threading
import time
import traceback

import Downloader.VersionsParser as VersionsParser
import DataMiners.DataMiners as DataMiners
import Utilities.Version as Version

LIMIT = 4

def datamine_version(version:Version.Version, dataminer_names:list[str], exceptions:dict[str,None|Exception]) -> None:
    try:
        for dataminer_name in dataminer_names:
            DataMiners.run_with_dependencies(version, dataminer_name, recalculate=False)
    except Exception as e:
        exceptions[version.name] = e
    else:
        exceptions[version.name] = None
        version.install_manager.all_done() # remove all of the installed client files from the version folder so I don't have to clog my storage

def trim_inactive_threads(threads:list[tuple[threading.Thread,Version.Version]]) -> list[threading.Thread]:
    '''Returns a new list containing the Threads from `threads` that are still alive.'''
    return [(thread, version) for thread, version in threads if thread.is_alive()]

def get_exceptions(threads:list[tuple[threading.Thread,Version.Version]], exceptions:dict[str,None|Exception]) -> dict[Version.Version,Exception]:
    '''Returns a list of Exceptions.'''
    return {version: exceptions[version.name] for thread, version in threads if (version.name in exceptions and exceptions[version.name] is not None)}

def main() -> None:
    dataminer_names = [dataminer_collection.name for dataminer_collection in DataMiners.dataminers]
    active_threads:list[tuple[threading.Thread,Version.Version]] = []
    exceptions:dict[str,None|Exception] = {} # {version.name: None|Exception}
    has_encountered_exception = False
    exception_versions:list[Version.Version] = []
    version_index = 0
    versions = list(reversed(VersionsParser.parse()))
    while len(active_threads) > 0 or (version_index < len(versions) and not has_encountered_exception):
        if version_index < len(versions):
            version = versions[version_index]
            version_index += 1
        while len(active_threads) >= LIMIT:

            # Exceptions
            local_exceptions = get_exceptions(active_threads, exceptions)
            if len(local_exceptions) > 0:
                for exception_version, exception in local_exceptions.items():
                    print("Version \"%s\" errored!" % exception_version.name)
                    traceback.print_exception(exception)
                has_encountered_exception = True # stop processing versions
                exception_versions.extend(local_exceptions.keys())

            # Waiting
            active_threads = trim_inactive_threads(active_threads)
            time.sleep(0.05)
        
        # New threads
        if version_index < len(versions) and not has_encountered_exception:
            if version.download_method is Version.DOWNLOAD_NONE:
                print("Skipped \"%s\" due to being unarchived." % version.name)
            else:
                print("Started \"%s\"." % version.name)
                new_thread = threading.Thread(target=datamine_version, args=[version, dataminer_names, exceptions])
                active_threads.append((new_thread, version))
                new_thread.start()
        time.sleep(0.05)
    if has_encountered_exception:
        raise RuntimeError("Versions [%s] errored!" % ", ".join("\"%s\"" % version.name for version in exception_versions))
