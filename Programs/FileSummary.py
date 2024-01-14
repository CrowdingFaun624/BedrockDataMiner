import Downloader.VersionsParser as VersionsParser

def main():
    version_names = VersionsParser.versions_dict
    selected_version_name = None
    while selected_version_name not in version_names:
        selected_version_name = input("Select a version to analyze: ")
    selected_version = version_names[selected_version_name]
    files = selected_version.install_manager.get_file_list()
    file_extensions:dict[str,int] = {}
    for file in files:
        file_name = file.split("/")[-1]
        if "." in file_name:
            file_extension = file_name.split(".")[-1]
        else:
            file_extension = ""
        if file_extension in file_extensions:
            file_extensions[file_extension] += 1
        else:
            file_extensions[file_extension] = 1
    sorted_file_extensions = {extension: count for count, extension in sorted([(count, extension) for extension, count in file_extensions.items()], reverse=True)}
    print("There are %i files overall in %s." % (len(files), selected_version.name))
    for extension, count in sorted_file_extensions.items():
        print("There are %i files with the \"%s\" extension." % (count, extension))
