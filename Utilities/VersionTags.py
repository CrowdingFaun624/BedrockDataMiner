import enum
from typing import Iterable

class VersionTag(enum.Enum):
    alpha      = "alpha"
    beta       = "beta"
    developer  = "developer"
    double_assets = "double-assets" # assigned by VersionsParser
    ipa        = "ipa"
    major      = "major"
    minor      = "minor"
    patch      = "patch"
    pocket_edition = "pocket-edition" # assigned by VersionsParser
    pocket_edition_alpha_before = "pocket-edition-alpha-before" # assigned by VersionsParser
    reupload   = "reupload"
    unreleased = "unreleased"

order_tags = [VersionTag.beta, VersionTag.major, VersionTag.minor, VersionTag.patch, VersionTag.reupload]
download_tracker_tags = [VersionTag.ipa]

def get_ordering_tag(tag_list:Iterable[VersionTag]) -> VersionTag:
    '''Returns the VersionTag from the list that is an order tag.'''
    if not isinstance(tag_list, Iterable): raise TypeError("`tag_list` is not an Iterable!")
    for tag in tag_list:
        if tag in order_tags: return tag
    else: raise IndexError("No ordering tags found within list!")
