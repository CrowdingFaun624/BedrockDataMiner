import Component.Importer as Importer
import Downloader.Accessor as Accessor
import Utilities.UserInput as UserInput


def main() -> None:
    version = UserInput.input_single(Importer.versions, "version")
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
