import threading
import time
import traceback

import DataMiners.DataMiners as DataMiners
import Downloader.VersionsParser as VersionsParser
import Utilities.Version as Version

LIMIT = 4

def datamine_version(version:Version.Version, dataminer_names:list[str], exceptions:dict[str,None|Exception]) -> None:
    try:
        for dataminer_name in dataminer_names:
            DataMiners.run_with_dependencies(version, dataminer_name)
    except Exception as e:
        exceptions[version.name] = e
    else:
        exceptions[version.name] = None
        if version.install_manager is not None and not version.latest:
            version.install_manager.all_done() # remove all of the installed client files from the version folder so I don't have to clog my storage

def trim_inactive_threads(threads:list[tuple[threading.Thread,Version.Version]]) -> list[tuple[threading.Thread,Version.Version]]:
    '''Returns a new list containing the Threads from `threads` that are still alive.'''
    return [(thread, version) for thread, version in threads if thread.is_alive()]

def get_exceptions(threads:list[tuple[threading.Thread,Version.Version]], exceptions:dict[str,None|Exception]) -> dict[Version.Version,Exception]:
    '''Returns a list of Exceptions.'''
    return {version: exception for thread, version in threads if (version.name in exceptions and (exception := exceptions[version.name]) is not None)}

def do_exception_stuff(active_threads:list[tuple[threading.Thread,Version.Version]], exceptions:dict[str,None|Exception], exception_versions:list[Version.Version]) -> bool:
    local_exceptions = get_exceptions(active_threads, exceptions)
    if len(local_exceptions) > 0:
        for exception_version, exception in local_exceptions.items():
            print("Version \"%s\" errored!" % exception_version.name)
            traceback.print_exception(exception)
            exception_versions.append(exception_version)
            # print("Added \"%s\" to exception versions, is now \"%s\"" % (exception_version, exception_versions))
        return True # stop processing versions
    return False

def main() -> None:
    dataminer_names = [dataminer_collection.name for dataminer_collection in DataMiners.dataminers]
    active_threads:list[tuple[threading.Thread,Version.Version]] = []
    exceptions:dict[str,None|Exception] = {} # {version.name: None|Exception}
    has_encountered_exception = False
    exception_versions:list[Version.Version] = []
    version_index = 0
    versions = list(reversed(VersionsParser.versions))
    while len(active_threads) > 0 or (version_index < len(versions) and not has_encountered_exception):
        if version_index < len(versions):
            version = versions[version_index]
            version_index += 1
        while len(active_threads) >= LIMIT:

            has_encountered_exception = do_exception_stuff(active_threads, exceptions, exception_versions) or has_encountered_exception
            if has_encountered_exception: break

            # Waiting
            active_threads = trim_inactive_threads(active_threads)
            time.sleep(0.05)

        has_encountered_exception = do_exception_stuff(active_threads, exceptions, exception_versions) or has_encountered_exception

        # New threads
        if version_index < len(versions) and not has_encountered_exception:
            assert not has_encountered_exception
            if version.download_method is Version.DownloadMethod.DOWNLOAD_NONE:
                print("Skipped \"%s\" due to being unarchived." % version.name)
            else:
                print("Started \"%s\"." % version.name)
                new_thread = threading.Thread(target=datamine_version, args=[version, dataminer_names, exceptions])
                active_threads.append((new_thread, version))
                new_thread.start()
        active_threads = trim_inactive_threads(active_threads)
        time.sleep(0.05)
    if has_encountered_exception:
        raise RuntimeError("Versions [%s] errored!" % ", ".join("\"%s\"" % version.name for version in exception_versions))
