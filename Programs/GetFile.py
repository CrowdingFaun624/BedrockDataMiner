import Component.Importer as Importer
import Downloader.Accessor as Accessor


def main() -> None:
    versions = Importer.versions
    version = None
    while version not in versions:
        version = input("Version: ")
    version = versions[version]
    file = input("File: ")
    install_manager = version.get_version_files_dict()["client"].get_accessor(required_type=Accessor.DirectoryAccessor)
    if install_manager is not None:
        destination = version.get_version_directory().joinpath(file)
        file_data = install_manager.read(file, "b")
        with open(destination, "wb") as destination_file:
            destination_file.write(file_data)
        print("File is in %s" % destination)
    else:
        print("Version \"%s\" is not archived." % version.name)
