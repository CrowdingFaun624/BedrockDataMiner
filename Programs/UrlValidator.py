import datetime
from typing import Callable, cast

import Component.Importer as Importer
import Downloader.DownloadManager as DownloadManager
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.Version as Version
import Version.VersionTag.VersionTag as VersionTag


def mcpedl_like_assembler(matcher_name:str) -> Callable[[Version.Version,str,dict[str,VersionTag.VersionTag]],list[str]]:

    def matches_mcpedl(version:Version.Version, url:str, version_tags:dict[str,VersionTag.VersionTag]) -> list[str]:
        VALID_ID_STARTS = ["minecraft-pe-", "minecraft-", "Minecraft-pe-", "Minecraft-PE-", "Minecraft-"] # make sure the more specific ones are first (e.g. "minecraft-pe-" before "minecraft-").
        if not url.startswith(KNOWN_URLS[matcher_name][0]):
            return ["%s url \"%s\" does not start with \"%s\"!" % (matcher_name, url, KNOWN_URLS[matcher_name][0])]
        stripped_url = url.replace(KNOWN_URLS[matcher_name][0], "")
        if "/" not in stripped_url:
            return ["%s stripped url \"%s\" does not have a \"/\"!" % (matcher_name, stripped_url)]
        if (slash_count := stripped_url.count("/")) > 1:
            return ["%s stripped url \"%s\" has too many \"/\" (count %i)!" % (matcher_name, stripped_url, slash_count)]
        date_string, id_string = stripped_url.split("/")

        try:
            day, month, year = date_string.split("-")
            date = datetime.date(int(year), int(month), int(day))
        except ValueError:
            return ["%s date string \"%s\" is invalid!" % (matcher_name, date_string)]

        for valid_id_start in VALID_ID_STARTS:
            if id_string.startswith(valid_id_start):
                stripped_id_string = id_string.replace(valid_id_start, "").replace(".apk", "")
                break
        else:
            return ["%s id string \"%s\" does not start validly!" % (matcher_name, id_string)]
        id = stripped_id_string.replace("-", ".")
        if version_tags["alpha"] in version.get_tags():
            id = "a" + id

        return_values:list[str] = []
        if date != version.time:
            return_values.append("Version \"%s\"'s date \"%s\" does not match its url's (%s) date of \"%s\"!" % (version.name, version.time, matcher_name, date))
        if id != version.name:
            return_values.append("Version \"%s\"'s id does not match its url's (%s) id of \"%s\"!" % (version.name, matcher_name, id))
        return return_values
    return matches_mcpedl

def matches_mcpealpha(version:Version.Version, url:str, version_tags:dict[str,VersionTag.VersionTag]) -> list[str]:
    matcher_name = "mcpealpha"
    if not url.startswith(KNOWN_URLS[matcher_name][0]):
        return ["%s url \"%s\" does not start with \"%s\"!" % (matcher_name, url, KNOWN_URLS[matcher_name][0])]
    stripped_url = url.replace(KNOWN_URLS[matcher_name][0], "")
    if not stripped_url.startswith("PE-"):
        return ["%s stripped url \"%s\" does not start with \"PE-\"" % (matcher_name, stripped_url)]
    if not stripped_url.endswith(".apk"):
        return ["%s stripped url \"%s\" does not end with \".apk\"" % (matcher_name, stripped_url)]
    id = stripped_url.replace("PE-", "").replace(".apk", "").replace("-", "_")

    return_values:list[str] = []
    if id != version.name.replace("-", "_"):
        return_values.append("Version \"%s\"'s id does not match its url's (%s) id of \"%s\"!" % (version.name, matcher_name, id))
    return return_values

def matches_minecraft_ios(version:Version.Version, url:str, version_tags:dict[str,VersionTag.VersionTag]) -> list[str]:
    matcher_name = "Minecraft-iOS"
    VALID_STARTS = ["Bedrock%20Edition%20-%20iOS/Minecraft%20", "Pocket%20Edition%20-%20iOS/Minecraft%20PE%20"]
    if not url.startswith(KNOWN_URLS[matcher_name][0]):
        return ["%s url \"%s\" does not start with \"%s\"!" % (matcher_name, url, KNOWN_URLS[matcher_name][0])]
    stripped_url = url.replace(KNOWN_URLS[matcher_name][0], "")
    for valid_start in VALID_STARTS:
        if stripped_url.startswith(valid_start):
            id_string = stripped_url.replace(valid_start, "")
            break
    else: return ["%s stripped url \"%s\" does not start with any valid start!" % (matcher_name, stripped_url)]
    if not id_string.endswith(".ipa"):
        return ["%s id string \"%s\" does not end with \".ipa\"!" % (matcher_name, id_string)]
    id = id_string.replace(".ipa", "")
    return_values:list[str] = []
    if id != version.name.replace("-", "_"):
        return_values.append("Version \"%s\"'s id does not match its url's (%s) id of \"%s\"!" % (version.name, matcher_name, id))
    return return_values

KNOWN_URLS:dict[str,tuple[str,Callable[[Version.Version,str,dict[str,VersionTag.VersionTag]],list[str]]]] = {
    "mcpedl": ("https://mcpedl.org/uploads_files/", mcpedl_like_assembler("mcpedl")),
    "planet-minecraft": ("https://planet-minecraft.com/uploads_files/", mcpedl_like_assembler("planet-minecraft")),
    "mcpealpha": ("https://archive.org/download/MCPEAlpha/", matches_mcpealpha),
    "Minecraft-iOS": ("https://archive.org/download/minecraft-iOS/Minecraft%20-%20iOS/", matches_minecraft_ios)
}

def validate(version:Version.Version, version_tags:dict[str,VersionTag.VersionTag]) -> list[str]:
    '''Returns a list of warning strings about the given version.'''
    try:
        accessor = cast(DownloadManager.DownloadManager, version.get_version_files_dict()["client"].get_accessor().manager)
    except Exceptions.VersionFileNoAccessorsError:
        return []
    if not hasattr(accessor, "url"):
        return []
    url = accessor.url
    for url_id, url_data in KNOWN_URLS.items():
        url_start, url_function = url_data
        if url.startswith(url_start):
            return url_function(version, url, version_tags)
    else: return ["Version \"%s\" has an unknown url \"%s\"!" % (version.name, url)]

def main() -> None:
    '''Writes a list of warning strings to "./_assets/version_parser_warnings.txt"'''
    versions = Importer.versions
    version_tags = Importer.version_tags
    warnings_list:list[str] = []
    for version in versions.values():
        if not version.get_version_files_dict()["client"].has_accessors(): continue
        warnings_list.extend(validate(version, version_tags))
    with open(FileManager.VERSION_PARSER_WARNINGS_FILE, "wt") as f:
        f.write("\n".join(warnings_list))
