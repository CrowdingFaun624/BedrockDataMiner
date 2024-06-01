import Version.VersionParser as VersionParser


def main() -> None:
    versions = VersionParser.versions
    version = None
    while version not in versions:
        version = input("Version: ")
    version = versions[version]
    file = input("File: ")
    install_manager = version.version_files["client"].accessors["download"]
    if install_manager is not None:
        assert version.version_directory is not None
        destination = version.version_directory.joinpath(file)
        file_promise = install_manager.get_file(file)
        with open(destination, "wb") as destination_file, file_promise.open() as source_file:
            destination_file.write(source_file.read())
        file_promise.all_done()
        print("File is in %s" % destination)
    else:
        print("Version \"%s\" is not archived." % version.name)
