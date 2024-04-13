import Downloader.VersionsParser as VersionsParser

def main() -> None:
    versions = VersionsParser.versions
    version = None
    while version not in versions:
        version = input("Version: ")
    version = versions[version]
    file = input("File: ")
    install_manager = version.install_manager
    if install_manager is not None:
        destination = install_manager.install(file)
        print("File is in %s" % destination)
    else:
        print("Version \"%s\" is not archived." % version.name)
