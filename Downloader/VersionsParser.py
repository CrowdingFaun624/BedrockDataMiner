import json
from typing import Any, Iterable, TYPE_CHECKING

import Downloader.UrlValidator as UrlValidator
import Downloader.DownloadManager as DownloadManager
import Downloader.StoredManager as StoredManager
import Downloader.LocalManager as LocalManager
import Utilities.FileManager as FileManager
import Utilities.Version as Version
import Utilities.VersionRange as VersionRange
import Utilities.VersionTags as VersionTags
from Utilities.FunctionCaller import FunctionCaller, WaitValue

if TYPE_CHECKING:
    import Downloader.InstallManager as InstallManager

INSTALL_MANAGERS:dict[str,type["InstallManager.InstallManager"]|None] = {
    Version.DownloadMethod.DOWNLOAD_FILE: StoredManager.StoredManager,
    Version.DownloadMethod.DOWNLOAD_LOCAL: LocalManager.LocalManager,
    Version.DownloadMethod.DOWNLOAD_NONE: None,
    Version.DownloadMethod.DOWNLOAD_URL: DownloadManager.DownloadManager,
}

def read_versions_file() -> Any:
    '''Returns the contents of '''
    path = FileManager.VERSIONS_FILE
    with open(path, "rt") as f:
        return json.load(f)
    
def is_valid_keys(keys:Iterable[str], possible_keys:Iterable[str], optional_keys:Iterable[str], strict_ordering:bool) -> bool:
    '''Checks the validity and order of the keys based off of the possible keys and the optional keys.'''
    for key in keys:
        if key not in possible_keys:
            return False
    required_keys = [possible_key for possible_key in possible_keys if possible_key not in optional_keys]
    for required_key in required_keys:
        if required_key not in keys:
            return False
    if not strict_ordering: return True
    used_keys = [possible_key for possible_key in possible_keys if possible_key in keys]
    if used_keys == keys: return True
    else: return False

def is_sorted(data:Iterable[Any]) -> bool:
    return all(a <= b for a, b in zip(data, data[1:]))

def verify_data_types(data:list[dict[str,str|list[str]]]) -> None:
    '''Raises a TypeError if the structure of `versions.json` is invalid.'''
    VALID_KEYS = ["id", "download", "parent", "time", "tags", "wiki_page", "development_categories"]
    OPTIONAL_KEYS = ["wiki_page", "development_categories"]
    NoneType = type(None)
    KEY_TYPES = {"id": str, "download": [NoneType, str], "parent": [NoneType, str], "time": [NoneType, str], "tags": list, "wiki_page": str, "development_categories": list}
    if not isinstance(data, list): raise TypeError("`data` is not a `list`!")
    for index, version_dict in enumerate(data):
        if not isinstance(version_dict, dict): raise TypeError("Item %i of `data` is not a `dict`!" % index)
        keys = list(version_dict.keys())
        if not is_valid_keys(keys, VALID_KEYS, OPTIONAL_KEYS, False):
            if "id" in version_dict and isinstance(version_dict["id"], str):
                raise TypeError("Invalid set of keys in version %s of `data`!" % version_dict["id"])
            else:
                raise TypeError("Invalid set of keys in item %i of `data`!" % index)
        version_name = version_dict["id"]
        if not is_valid_keys(keys, VALID_KEYS, OPTIONAL_KEYS, True):
            raise TypeError("Keys \"%s\" are not in order in version %s of `data`!" % (str(keys), version_name))
        
        for key, key_type in KEY_TYPES.items():
            if key not in keys: continue
            if isinstance(key_type, Iterable):
                if not any(isinstance(key, key_subtype) for key_subtype in key_type):
                    raise TypeError("Key \"%s\" of version %s of `data` is not any of %s!" % (key, version_name, str(key_type)))
            else:
                if not isinstance(version_dict[key], key_type):
                    raise TypeError("Key \"%s\" of version %s of `data` is not a %s!" % (key, version_name, str(key_type)))
        for tag_index, tag in enumerate(version_dict["tags"]):
            if not isinstance(tag, str):
                raise TypeError("Tag %i of version %s of `data` is not a str!" % (tag_index, version_name))
        if not is_sorted(version_dict["tags"]):
            raise TypeError("Tags in version \"%s\" of `data` is not sorted!" % version_name)
        if "development_categories" in version_dict:
            for development_category_index, development_category in enumerate(version_dict["development_categories"]):
                if not isinstance(development_category, str):
                    raise TypeError("Development categorie %i of version %s of `data` is not a str!" % (development_category_index, version_name))
            if not is_sorted(version_dict["development_categories"]):
                raise TypeError("Development categories in version \"%s\" of `data` is not sorted!" % version_name)

def assign_parents(versions:list[Version.Version]) -> None:
    '''Calls `assign_parent` on all versions, giving them a link to another version.'''
    versions_dict = {version.name: version for version in versions}
    for version in versions:
        version.assign_parent(versions_dict)

def verify_ordering(versions:list[Version.Version]) -> None:
    '''Raises a ValueError if the ordering of the versions is incorrect in any way.'''
    ORDERING_TAGS = set(VersionTags.order_tags)
    ORDER = [VersionTags.VersionTag.beta, VersionTags.VersionTag.major, {VersionTags.VersionTag.minor, VersionTags.VersionTag.patch, VersionTags.VersionTag.reupload}]
    ALLOWED_CHILDREN = {
        VersionTags.VersionTag.beta: [VersionTags.VersionTag.reupload],
        VersionTags.VersionTag.major: [VersionTags.VersionTag.beta, VersionTags.VersionTag.minor, VersionTags.VersionTag.patch, VersionTags.VersionTag.reupload],
        VersionTags.VersionTag.minor: [VersionTags.VersionTag.beta, VersionTags.VersionTag.patch, VersionTags.VersionTag.reupload],
        VersionTags.VersionTag.patch: [VersionTags.VersionTag.reupload],
        VersionTags.VersionTag.reupload: []}
    TOP_LEVEL_TAG = VersionTags.VersionTag.major
    BEFORE_TAGS = [VersionTags.VersionTag.beta]
    AFTER_TAGS = [VersionTags.VersionTag.minor, VersionTags.VersionTag.patch, VersionTags.VersionTag.reupload]

    for version in versions:
        if (order_tag_count := sum(order_tag in version.tags for order_tag in ORDERING_TAGS)) != 1:
            if order_tag_count < 1: raise ValueError("Version %s has no ordering tags!" % version.name)
            else: raise ValueError("Version %s has too many ordering tags (>1)!" % version.name)
    
    top_level_versions = [version for version in versions if version.parent is None] # versions with no parents
    top_level_childrens:list[Version.Version] = []
    for version in top_level_versions:
        top_level_childrens.extend(version.get_children_recursive())
    if len(set(top_level_childrens)) != len(top_level_childrens):
        already_seen_versions:set[Version.Version] = set()
        for version in top_level_childrens:
            if version in already_seen_versions: raise ValueError("Version \"%s\" is a child of multiple top-level versions!")
            else: already_seen_versions.add(version)
        else: raise ValueError("A duplicate version exists, but unable to find it!")
    
    for version in top_level_versions:
        if TOP_LEVEL_TAG not in version.tags:
            raise ValueError("Version \"%s\" is a top-level version but is not %s!" % (version.name, TOP_LEVEL_TAG))
    for version in versions:
        version_order_tag = version.ordering_tag
        for child in version.children:
            child_order_tag = child.ordering_tag
            if child_order_tag not in ALLOWED_CHILDREN[version_order_tag]:
                raise ValueError("Version \"%s\" (type \"%s\"), child of \"%s\" (type \"%s\") is not a valid child type of a \"%s\"!"% (child.name, child_order_tag, version.name, version_order_tag, version_order_tag))
    def order_contains_at_index(ordering_tag:VersionTags.VersionTag) -> bool:
        return (not isinstance(ORDER[order_index], Iterable) and ordering_tag == ORDER[order_index]) or (isinstance(ORDER[order_index], Iterable) and ordering_tag in ORDER[order_index])
    for version in versions:
        order_index = 0
        for child in version.children:
            while not order_contains_at_index(child.ordering_tag):
                order_index += 1
                if order_index >= len(ORDER):
                    raise ValueError("Version \"%s\"'s children, %s, are in an invalid order at child \"%s\"!" % (version.name, str([child.ordering_tag for child in version.children]), child.name))
            # after this while loop, `order_index` must be a value such that child.ordering_tag == or in ORDER[order_index].
    for version in versions:
        previous_time = None
        previous_child = None # for error messages
        for child in version.children:
            if child.ordering_tag in BEFORE_TAGS:
                if version.time is not None and child.time is not None and child.time > version.time:
                    raise ValueError("Child \"%s\" (type \"%s\") of \"%s\" (type \"%s\") comes after the latter!" % (child.name, child.ordering_tag, version.name, version.ordering_tag))
            elif child.ordering_tag in AFTER_TAGS:
                if version.time is not None and child.time is not None and child.time < version.time:
                    raise ValueError("Child \"%s\" (type \"%s\") of \"%s\" (type \"%s\") comes before the latter!" % (child.name, child.ordering_tag, version.name, version.ordering_tag))
            if previous_time is not None:
                if child.time is not None and child.time < previous_time:
                    raise ValueError("Child \"%s\"'s date (\"%s\") comes after child \"%s\"'s date (\"%s\") despite being before it in the children of \"%s\"!" % (previous_child.name, previous_time, child.name, child.time, version.name))
            previous_time = child.time
            previous_child = child

def assign_wiki_pages(versions:list[Version.Version]) -> None:
    '''Calls `assign_wiki_page` on all versions.'''
    for version in versions:
        version.assign_wiki_page()

def assign_install_managers(versions:list[Version.Version]) -> None:
    '''Sets the `install_manager` attribute to its corresponding InstallManager.'''
    for version in versions:
        install_manager_type = INSTALL_MANAGERS[version.download_method]
        if install_manager_type is None:
            version.install_manager = None
        else:
            version.install_manager = install_manager_type(version, FileManager.get_version_install_path(version.version_folder))

def assign_additional_tags(versions:list[Version.Version]) -> None:
    '''Assigns tags that are assigned by the VersionsParser'''
    version_dict = {version.name: version for version in versions}
    double_assets_range = VersionRange.VersionRange(version_dict["1.20.50.21"], "-")
    pocket_edition_ranges = VersionRange.VersionRange("-", version_dict["1.1.7"])
    pocket_edition_alpha_before = VersionRange.VersionRange(version_dict["a0.17.0.1"], version_dict["1.1.7"])
    for version in versions:
        if version in double_assets_range and VersionTags.VersionTag.ipa not in version.tags:
            version.add_tag(VersionTags.VersionTag.double_assets)
        if version in pocket_edition_ranges:
            version.add_tag(VersionTags.VersionTag.pocket_edition)
        if version in pocket_edition_alpha_before:
            version.add_tag(VersionTags.VersionTag.pocket_edition_alpha_before)

def parse() -> list[Version.Version]:
    data = read_versions_file()
    verify_data_types(data)
    versions:list[Version.Version] = []
    already_names:set[str] = set()
    already_downloads:set[str] = set()
    for index, version_dict in enumerate(data):
        id:str = version_dict["id"]
        download:str|None = version_dict["download"]
        parent:str|None = version_dict["parent"]
        time:str|None = version_dict["time"]
        tags:list[str] = version_dict["tags"]
        wiki_page:str|None = version_dict["wiki_page"] if "wiki_page" in version_dict else None
        development_categories:list[str]|None = version_dict["development_categories"] if "development_categories" in version_dict else None
        versions.append(Version.Version(id, download, parent, time, tags, index, wiki_page, development_categories))

        if id in already_names:
            raise KeyError("Version named \"%s\" already exists!" % id)
        if download is not None and download in already_downloads:
            raise KeyError("Version with download \"%s\" already exists!" % download)
        already_names.add(id)
        already_downloads.add(download)

    assign_parents(versions)
    verify_ordering(versions)
    assign_additional_tags(versions)
    assign_wiki_pages(versions)
    assign_install_managers(versions)
    UrlValidator.validate_url_data(versions)
    fix_folders(versions)
    return versions

def fix_folders(versions:list[Version.Version]) -> None:
    '''Makes folders that are empty and don't exist disappear.
    It is for scenarios like when a version is delayed and betas suddenly point to a new parent,
    or when a version is renamed.'''
    versions_dict = {version.name: version for version in versions}
    for version_folder in FileManager.VERSIONS_FOLDER.iterdir():
        if not version_folder.is_dir(): continue
        if version_folder.name not in versions_dict:
            if sum(1 for child in version_folder.iterdir()) == 0:
                version_folder.rmdir()
            else:
                print("Version folder \"%s\" does not exist in versions.json and contains files!")

def get_version_dict() -> dict[str,Version.Version]:
    return {version.name: version for version in versions.get()}

versions = WaitValue(FunctionCaller(parse))
versions_dict = WaitValue(FunctionCaller(get_version_dict))

def main() -> None:
    parse()
