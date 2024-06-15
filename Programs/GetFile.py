import Component.Importer as Importer


def main() -> None:
    versions = Importer.versions
    version = None
    while version not in versions:
        version = input("Version: ")
    version = versions[version]
    file = input("File: ")
    install_manager = version.get_version_files_dict()["client"].get_accessor()
    if install_manager is not None:
        destination = version.get_version_directory().joinpath(file)
        file_promise = install_manager.get_file(file)
        with open(destination, "wb") as destination_file, file_promise.open() as source_file:
            destination_file.write(source_file.read())
        file_promise.all_done()
        print("File is in %s" % destination)
    else:
        print("Version \"%s\" is not archived." % version.name)
