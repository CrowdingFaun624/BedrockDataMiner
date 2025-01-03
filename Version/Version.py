import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Version.VersionFile as VersionFile
import Version.VersionTag.VersionTag as VersionTag

if TYPE_CHECKING:
    import Downloader.Accessor as Accessor

class Version():

    def __init__(self, name:str, domain:"Domain.Domain", time:datetime.datetime|None, index:int) -> None:
        self.name = name
        self.time = time
        self.index = index

        self.parent:Version|None = None
        self.tags:list[VersionTag.VersionTag]|None = None
        self.tags_str:list[str]|None = None
        self.version_files:list[VersionFile.VersionFile]|None = None
        self.latest = False
        self.released = True
        self.order_tag:VersionTag.VersionTag|None = None

        self.version_directory = domain.versions_directory.joinpath(self.name)
        self.data_directory = self.version_directory.joinpath("data")
        self.version_directory.mkdir(exist_ok=True)
        self.children:list[Version] = []

    def link_finals(
        self,
        parent:"Version|None",
        tags:list[VersionTag.VersionTag],
        version_files:list[VersionFile.VersionFile],
    ) -> None:
        self.parent = parent
        self.tags = tags
        self.tags_str = [tag.name for tag in self.tags]
        self.version_files = version_files

        if self.parent is not None:
            self.parent.add_child(self)

    def assign_latest(self) -> None:
        "Makes this Version be a latest one."
        self.latest = True

    def finalize(self) -> None:
        self.tags_dict = {tag.name: tag for tag in self.get_tags()}
        self.version_files_dict = {version_file.get_version_file_type().name: version_file for version_file in self.get_version_files()}
        for tag in self.get_tags():
            if self.order_tag is None and tag.is_order_tag:
                self.order_tag = tag
            if tag.is_unreleased_tag:
                self.released = False
        if self.order_tag is None:
            raise Exceptions.NoOrderVersionTagsFoundError(self, self.get_tags())

    def get_tags(self) -> list[VersionTag.VersionTag]:
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        return self.tags

    def get_tags_str(self) -> list[str]:
        if self.tags_str is None:
            raise Exceptions.AttributeNoneError("tags_str", self)
        return self.tags_str

    def get_order_tag(self) -> VersionTag.VersionTag:
        if self.order_tag is None:
            raise Exceptions.AttributeNoneError("order_tag", self)
        return self.order_tag

    def get_tags_dict(self) -> dict[str,VersionTag.VersionTag]:
        if self.tags_dict is None:
            raise Exceptions.AttributeNoneError("tags_dict", self)
        return self.tags_dict

    def get_version_files(self) -> list[VersionFile.VersionFile]:
        if self.version_files is None:
            raise Exceptions.AttributeNoneError("files", self)
        return self.version_files

    def get_version_files_dict(self) -> dict[str,VersionFile.VersionFile]:
        if self.version_files_dict is None:
            raise Exceptions.AttributeNoneError("version_files_dict", self)
        return self.version_files_dict

    def get_accessor[a: Accessor.Accessor](self, file_type:str, required_type:type[a]) -> a|None:
        return self.get_version_files_dict()[file_type].get_accessor(True, required_type=required_type)

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

    def has_tag(self, search_tag:VersionTag.VersionTag|str) -> bool:
        '''
        Returns True if this Version has the given VersionTag.
        :search_tag: The VersionTag (or name of the VersionTag) to search this Version for.
        '''
        if isinstance(search_tag, str):
            return search_tag in self.get_tags_str()
        else:
            return search_tag in self.get_tags()

    def add_tag(self, tag:VersionTag.VersionTag) -> None:
        '''Adds a tag to the Version.'''
        tags_list, tags_dict = self.get_tags(), self.get_tags_dict()
        if tag not in tags_dict:
            tags_list.append(tag)
            tags_dict[tag.name] = tag

    def get_children_recursive(self) -> list["Version"]:
        children = self.children[:]
        for child in self.children:
            children.extend(child.children)
        return children

    def add_child(self, child:"Version") -> None:
        self.children.append(child)

    def get_version_directory(self) -> Path:
        self.version_directory.mkdir(exist_ok=True)
        return self.version_directory

    def get_data_directory(self) -> Path:
        self.data_directory.mkdir(exist_ok=True)
        return self.data_directory

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Version {self.name}>"

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
