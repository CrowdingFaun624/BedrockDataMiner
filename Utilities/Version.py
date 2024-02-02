import datetime
from pathlib2 import Path
from typing import TYPE_CHECKING
import validators

import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager as StoredVersionsManager
import Utilities.VersionTags as VersionTags

if TYPE_CHECKING:
    import Downloader.InstallManager as InstallManager

DOWNLOAD_NONE = None
DOWNLOAD_URL = "url"
DOWNLOAD_FILE = "file"
DOWNLOAD_LOCAL = "local"

class Version():
    def __init__(self, name:str, download_link:str|None, parent_str:str|None, time_str:str|None, tags_str:list[VersionTags.VersionTag], index:int, wiki_page:str|None=None, development_categories:list[str]|None=None) -> None:
        self.name = name
        self.download_link = download_link
        self.parent_str = parent_str
        self.time_str = time_str
        self.tags_str = tags_str
        self.index = index
        self.wiki_page = wiki_page
        self.development_category_names = development_categories

        # attributes set in this __init__ function.
        self.download_method:str = None
        self.version_folder:Path = None

        # attributes to be set after finished creating version list.

        self.children:list[Version] = []
        self.siblings:list[Version]|None = None
        self.parent:"Version"|None = None
        self.time:datetime.date|None = None
        self.ordering_tag:str = None
        self.install_manager:InstallManager.InstallManager|None = None

        self.validate_name()
        self.validate_download_link()
        self.validate_parent()
        self.validate_time()
        self.validate_tags()

    def assign_wiki_page(self) -> None:
        '''Sets this Version's `wiki_page` attribute.'''
        alpha = ""
        if VersionTags.VersionTag.pocket_edition not in self.tags:
            edition = "Bedrock Edition"
            alpha_positioned_before = True
            if self.ordering_tag is VersionTags.VersionTag.beta:
                alpha = " beta"
            development_category_suffix = " betas"
        else:
            edition = "Pocket Edition"
            alpha_positioned_before = VersionTags.VersionTag.pocket_edition_alpha_before in self.tags
            if VersionTags.VersionTag.alpha in self.tags or self.ordering_tag is VersionTags.VersionTag.beta:
                alpha = " alpha"
            elif self.ordering_tag is VersionTags.VersionTag.beta:
                alpha = " beta"
            development_category_suffix = " builds"
            
        if "_build" in self.name:
            build = " build " + self.name.split("_build")[1]
        else: build = ""
        trimmed_name = "".join(char for char in self.name.split("_")[0].split("-")[0] if char in "0123456789.")
        if alpha_positioned_before:
            page_name = edition + alpha + " " + trimmed_name + build
        else:
            page_name = edition + " v" + trimmed_name + alpha + build
        if self.wiki_page is None: self.wiki_page = page_name
        development_category_name = "Category:" + self.wiki_page + development_category_suffix
        if self.development_category_names is None: self.development_category_names = [development_category_name]
    
    def add_tag(self, tag:VersionTags.VersionTag) -> None:
        '''Adds a tag to the Version.'''
        if not isinstance(tag, VersionTags.VersionTag):
            raise TypeError("Attempted to add a non-VersionTag object to \"%s\"'s tags!" % (self.name))
        if tag not in self.tags:
            self.tags.append(tag)

    def validate_version_name(self, name:str) -> None:
        '''Raises a ValueError if it is not valid, or a TypeError if `name` is the wrong type.'''
        if not isinstance(name, str): raise TypeError("`name` is not a `str`!")
        version_folder = Path(FileManager.VERSIONS_FOLDER.joinpath(name))
        if version_folder.parent != FileManager.VERSIONS_FOLDER: raise ValueError("Invalid Version name \"%s\"!" % str(name))

    def validate_name(self) -> None:
        '''Sets this Version's `version_folder` attribute based off of the value of `name`. Raises a ValueError if it is not valid, or a TypeError if `name` is the wrong type.'''
        if not isinstance(self.name, str): raise TypeError("`name` is not a `str`!")
        self.version_folder = FileManager.get_version_path(self.name)
        self.validate_version_name(self.name)
        self.version_folder.mkdir(exist_ok=True)

    def validate_download_link(self) -> None:
        '''Sets this Version's `download_method` attribute based off of the value of `download_link`.
        Raises a ValueError if it is not valid, or a TypeError if `download_link` is the wrong type.'''
        if self.download_link is None:
            self.download_method = DOWNLOAD_NONE
            return
        if not isinstance(self.download_link, str): raise TypeError("`download_link` is not a `str`!")
        if validators.url(self.download_link):
            self.download_method = DOWNLOAD_URL
        elif self.download_link.startswith("/") and StoredVersionsManager.version_exists(self.download_link[1:]):
            self.download_method = DOWNLOAD_FILE
        elif self.download_link in ("release_local", "beta_local"):
            self.download_method = DOWNLOAD_LOCAL
        else:
            raise ValueError("Download link \"%s\" is not valid!" % self.download_link)

    def validate_parent(self) -> None:
        '''Raises a ValueError if it is not valid, or a TypeError if it is the wrong type.'''
        if self.parent_str is None: return
        if self.parent_str == self.name: raise ValueError("Parent version of \"%s\" is itself!" % self.name)
        return self.validate_version_name(self.parent_str)

    def validate_time(self) -> None:
        '''Raises a ValueError if it is not valid, or a TypeError if it is the wrong type.'''
        if self.time_str is None:
            self.time = None
            return
        if not isinstance(self.time_str, str): raise TypeError("`time_str` is not a `str`!")
        self.time = datetime.date.fromisoformat(self.time_str)
        if self.time > datetime.date.today(): raise ValueError("`time` is after today!")
        if self.time.year < 2011: raise ValueError("`time` is before year 2011!")

    def validate_tags(self) -> None:
        '''Raises a ValueError if this Version's tags are not valid.'''
        self.tags = [VersionTags.VersionTag[tag_str] for tag_str in self.tags_str]
        if not all(isinstance(tag, VersionTags.VersionTag) for tag in self.tags):
            raise ValueError("Version \"%s\" does not have valid VersionTags: \"%s\"!" % (self.name, str(self.tags)))
        self.ordering_tag = VersionTags.get_ordering_tag(self.tags)
        if VersionTags.VersionTag.unreleased in self.tags:
            if self.download_method is not DOWNLOAD_NONE:
                raise ValueError("Version \"%s\" has the \"%s\" tag but has a download method!" % (self.name, VersionTags.VersionTag.unreleased))
    
    def get_children_recursive(self) -> list["Version"]:
        children = self.children[:]
        for child in self.children:
            children.extend(child.children)
        return children

    def add_child(self, child:"Version") -> None:
        self.children.append(child)

    def assign_parent(self, version_dict:dict[str,"Version"]) -> None:
        if not isinstance(version_dict, dict): raise TypeError("`version_dict` is not a dict for version \"%s\"!" % self.name)
        if self.parent_str is None:
            self.parent = None
            return
        if self.parent_str not in version_dict:
            raise KeyError("Unable to find parent \"%s\" of version \"%s\"!" % (self.parent_str, self.name))
        self.parent = version_dict[self.parent_str]
        self.parent.add_child(self)
        self.siblings = self.parent.children

    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        return "<Version %s>" % self.name
    
    def __hash__(self) -> int:
        return hash((self.index, self.name, self.download_link, self.parent_str, self.time_str))
    
    def __lt__(self, other:"Version") -> bool:
        if not isinstance(other, Version):
            raise TypeError("Attempted to compare a Version to \"%s\"" % str(type(other)))
        return self.index < other.index
    def __gt__(self, other:"Version") -> bool:
        if not isinstance(other, Version):
            raise TypeError("Attempted to compare a Version to \"%s\"" % str(type(other)))
        return self.index > other.index
    def __le__(self, other:"Version") -> bool:
        if not isinstance(other, Version):
            raise TypeError("Attempted to compare a Version to \"%s\"" % str(type(other)))
        return self.index <= other.index
    def __ge__(self, other:"Version") -> bool:
        if not isinstance(other, Version):
            raise TypeError("Attempted to compare a Version to \"%s\"" % str(type(other)))
        return self.index >= other.index
