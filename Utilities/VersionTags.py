from typing import Any, Iterable

class VersionTag(str): ...

ALPHA      = VersionTag("alpha")
BETA       = VersionTag("beta")
DEVELOPER  = VersionTag("developer")
DOUBLE_ASSETS = VersionTag("double-assets") # assigned by VersionParser
IPA        = VersionTag("ipa")
MAJOR      = VersionTag("major")
MINOR      = VersionTag("minor")
PATCH      = VersionTag("patch")
POCKET_EDITION = VersionTag("pocket-edition") # assigned by VersionParser
POCKET_EDITION_ALPHA_BEFORE = VersionTag("pocket-edition-alpha-before") # assigned by VersionParser
REUPLOAD   = VersionTag("reupload")
UNRELEASED = VersionTag("unreleased")

tag_list = [ALPHA, BETA, DEVELOPER, IPA, MAJOR, MINOR, PATCH, REUPLOAD, UNRELEASED]
order_tags = [BETA, MAJOR, MINOR, PATCH, REUPLOAD]
download_tracker_tags = [IPA]

def get_ordering_tag(tag_list:Iterable[VersionTag]) -> VersionTag:
    '''Returns the VersionTag from the list that is an order tag.'''
    if not isinstance(tag_list, Iterable): raise TypeError("`tag_list` is not an Iterable!")
    for tag in tag_list:
        if tag in order_tags: return tag
    else: raise IndexError("No ordering tags found within list!")

def get_tag(name:str) -> str:
    '''Returns the exact VersionTag object that matches with the input tag.'''
    if is_valid_tag(name):
        return tag_list[tag_list.index(name)]
    else:
        raise KeyError("VersionTag with name of \"%s\" not found in list!" % name)

def get_tags(names:Iterable[str]) -> list[VersionTag]:
    '''Returns the exact VersionTag objects that match with the input tags.'''
    if not isinstance(names, Iterable):
        raise TypeError("`names` is not an Iterable!")
    return [get_tag(name) for name in names]

def is_valid_tag(name:str) -> bool:
    '''Returns if a string matching a string in the tag list exists.'''
    return name in tag_list

def is_tag(tag:Any) -> bool:
    '''Returns True if the given tag is a VersionTag object.'''
    return isinstance(tag, VersionTag)

def is_tags(tags:Iterable[Any]) -> bool:
    '''Returns True if all tags in the list are VersionTag objects.'''
    if not isinstance(tags, Iterable): return False
    return all(is_tag(tag) for tag in tags)