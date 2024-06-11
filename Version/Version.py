import datetime
from typing import TYPE_CHECKING, Any

from pathlib2 import Path

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.VersionFile as VersionFile
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Downloader.Accessor as Accessor

class Version():

    def __init__(self, name:str, files:dict[str,dict[str,Any]], parent_str:str|None, time_str:str|None, tags_str:list[str], index:int, version_tags:VersionTags.VersionTags) -> None:
        self.name = name
        self.files_str = files
        self.parent_str = parent_str
        self.time_str = time_str
        self.tags_str = tags_str
        self.index = index

        # attributes set in this __init__ function.
        self.version_directory:Path|None = None
        self.version_files:dict[str,VersionFile.VersionFile] = {}

        # attributes to be set after finished creating version list.
        self.children:list[Version] = []
        self.siblings:list[Version]|None = None
        self.parent:"Version|None" = None
        self.time:datetime.date|None = None
        self.ordering_tag:VersionTags.VersionTag|None = None
        self.latest = False

        self.validate_name()
        self.validate_tags(version_tags)
        self.validate_parent()
        self.validate_time()

    def get_accessor(self, file_type:str) -> "Accessor.Accessor":
        return self.version_files[file_type].get_accessor()

    # this will be needed when I actually finish redoing the wiki page thing
    # def assign_wiki_page(self, version_tags:VersionTags.VersionTags) -> None:
    #     '''Sets this Version's `wiki_page` attribute.'''
    #     alpha = ""
    #     if version_tags["pocket_edition"] not in self.tags:
    #         edition = "Bedrock Edition"
    #         alpha_positioned_before = True
    #         if self.ordering_tag is version_tags["beta"]:
    #             alpha = " beta"
    #         development_category_suffix = " betas"
    #     else:
    #         edition = "Pocket Edition"
    #         alpha_positioned_before = version_tags["pocket_edition_alpha_before"] in self.tags
    #         if version_tags["alpha"] in self.tags or self.ordering_tag is version_tags["beta"]:
    #             alpha = " alpha"
    #         elif self.ordering_tag is version_tags["beta"]:
    #             alpha = " beta"
    #         development_category_suffix = " builds"

    #     if "_build" in self.name:
    #         build = " build " + self.name.split("_build")[1]
    #     else: build = ""
    #     trimmed_name = "".join(char for char in self.name.split("_")[0].split("-")[0] if char in "0123456789.")
    #     if alpha_positioned_before:
    #         page_name = edition + alpha + " " + trimmed_name + build
    #     else:
    #         page_name = edition + " v" + trimmed_name + alpha + build
    #     if self.wiki_page is None: self.wiki_page = page_name
    #     development_category_name = "Category:" + self.wiki_page + development_category_suffix
    #     if self.development_category_names is None: self.development_category_names = [development_category_name]

    def add_tag(self, tag:VersionTags.VersionTag) -> None:
        '''Adds a tag to the Version.'''
        if tag not in self.tags:
            self.tags.append(tag)

    def validate_version_name(self, name:str) -> None:
        '''Raises an InvalidVersionNameError if it is not valid.'''
        version_directory = FileManager.VERSIONS_DIRECTORY.joinpath(name)
        if version_directory.parent != FileManager.VERSIONS_DIRECTORY: raise Exceptions.InvalidVersionNameError(self)

    def validate_name(self) -> None:
        '''Sets this Version's `version_directory` attribute based off of the value of `name`. Raises an InvalidVersionNameError if it is not valid.'''
        self.version_directory = FileManager.get_version_path(self.name)
        self.validate_version_name(self.name)
        self.version_directory.mkdir(exist_ok=True)

    def validate_parent(self) -> None:
        '''Raises a InvalidParentVersionError if it is not valid.'''
        if self.parent_str is None: return
        if self.parent_str == self.name:
            raise Exceptions.InvalidParentVersionError(self, self.parent_str)

    def validate_time(self) -> None:
        '''Raises an InvalidVersionTimeError if it is not valid.'''
        if self.time_str is None:
            self.time = None
            return
        self.time = datetime.date.fromisoformat(self.time_str)
        if self.time > datetime.date.today(): raise Exceptions.InvalidVersionTimeError(self, self.time, "time is after today")
        # TODO: remove this line or make it ✨data-based✨
        if self.time.year < 2011: raise Exceptions.InvalidVersionTimeError(self, self.time, "time is before 2011")

    def validate_tags(self, version_tags:VersionTags.VersionTags) -> None:
        self.tags = [version_tags[tag_str] for tag_str in self.tags_str]
        self.ordering_tag = VersionTags.get_ordering_tag(self.tags)

    def get_children_recursive(self) -> list["Version"]:
        children = self.children[:]
        for child in self.children:
            children.extend(child.children)
        return children

    def add_child(self, child:"Version") -> None:
        self.children.append(child)

    def assign_files(self, version_file_types:dict[str,VersionFileType.VersionFileType], auto_assigning_version_file_types:list[VersionFileType.VersionFileType], version_tags:VersionTags.VersionTags) -> None:
        for file_type_name, accessors in self.files_str.items():
            file_type = version_file_types.get(file_type_name, None)
            if file_type is None:
                raise Exceptions.UnrecognizedVersionFileTypeError(file_type_name, self)
            self.version_files[file_type_name] = VersionFile.VersionFile(self, file_type, accessors, version_tags)
        for auto_assigning_version_file_type in auto_assigning_version_file_types:
            if auto_assigning_version_file_type.name in self.version_files: continue
            else:
                if auto_assigning_version_file_type.auto_assign is None:
                    raise Exceptions.InvalidStateError()
                auto_assigning_accessors = {auto_assigning_version_file_type.auto_assign["accessor"]: auto_assigning_version_file_type.auto_assign["parameters"]}
                self.version_files[auto_assigning_version_file_type.name] = VersionFile.VersionFile(self, auto_assigning_version_file_type, auto_assigning_accessors, version_tags)
        for file_type_name, file_type in version_file_types.items():
            if file_type.must_exist and file_type_name not in self.version_files:
                raise Exceptions.RequiredVersionFileTypeMissingError(file_type, self)

        if version_tags["unreleased"] in self.tags:
            if len(self.version_files) == 0:
                raise Exceptions.UnreleasedDownloadableVersionError(self, version_tags["unreleased"])

    def assign_parent(self, version_dict:dict[str,"Version"]) -> None:
        if self.parent_str is None:
            self.parent = None
            return
        if self.parent_str not in version_dict:
            raise Exceptions.UnrecognizedVersionError(self.parent_str, self, "(parent of Version)")
        self.parent = version_dict[self.parent_str]
        self.parent.add_child(self)
        self.siblings = self.parent.children

    def get_version_directory(self) -> Path:
        '''Returns this Version's directory, and raises an error if it does not exist.'''
        if self.version_directory is None:
            raise Exceptions.AttributeNoneError("version_directory", self)
        return self.version_directory

    def get_order_tag(self) -> VersionTags.VersionTag:
        '''Returns this Version's ordering VersionTag, and raises an error if it does not exist.'''
        if self.ordering_tag is None:
            raise Exceptions.AttributeNoneError("ordering_tag", self)
        return self.ordering_tag

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "<Version %s>" % self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __lt__(self, other:"Version") -> bool:
        return self.index < other.index

    def __gt__(self, other:"Version") -> bool:
        return self.index > other.index

    def __le__(self, other:"Version") -> bool:
        return self.index <= other.index

    def __ge__(self, other:"Version") -> bool:
        return self.index >= other.index
