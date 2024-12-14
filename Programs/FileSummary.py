import Component.Importer as Importer
import Downloader.Accessor as Accessor
import Utilities.UserInput as UserInput


def main():
    selected_version = UserInput.input_single(Importer.versions, "version")
    files = selected_version.get_version_files_dict()["client"].get_accessor(required_type=Accessor.DirectoryAccessor).get_full_file_list()
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
