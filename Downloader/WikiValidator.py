import datetime
import time

import Downloader.VersionsParser as VersionsParser
import Utilities.FileManager as FileManager
import Utilities.Version as Version
import Utilities.VersionTags as VersionTags

try:
    import mediawikiapi
    api_is_working = True
except:
    api_is_working = False

def get_wikitext(page:mediawikiapi.WikipediaPage) -> str:
    '''Returns the wikitext stored on a particular page.'''
    if not getattr(page, "_wikitext", False):
        query_params: dict[str,str|int] = {
            "prop": "revisions",
            "rvslots": "*",
            "rvprop": "content",
            "formatversion": "2",
            "titles": page.title
        }
        request = page.request(query_params)
        try:
            page_data = request["query"]["pages"][0]
        except KeyError:
            raise KeyError("Weird json from \"%s\": \"%s\"!" % (page.title, str(request)))
        if "missing" in page_data and page_data["missing"] is True:
            raise FileNotFoundError("Page \"%s\" does not exist on the Minecraft Wiki!" % page.title)
        page._wikitext = page_data["revisions"][0]["slots"]["main"]["content"]
    if page._wikitext == "":
        raise RuntimeError("Page \"%s\" is empty!" % page.title)
    return page._wikitext

def get_category_members(page:mediawikiapi.WikipediaPage) -> list[str]:
    '''Returns a list of page titles on the particular category page.'''
    if not getattr(page, "_members", False):
        members:list[str] = []
        continuation = None
        completed_continuation = False
        while not completed_continuation:
            query_params:dict[str,str|int] = {
                "list": "categorymembers",
                "cmtitle": page.title,
            }
            if continuation is not None: query_params.update(continuation)
            request = page.request(query_params)
            if "continue" in request:
                continuation = request["continue"]
                completed_continuation = False
                time.sleep(0.05)
            else: completed_continuation = True
            members.extend(member["title"] for member in request["query"]["categorymembers"])
        page._members = members
    return page._members

def get_infobox_data(wikitext:str, version:Version.Version) -> dict[str,str]:
    '''Returns the contents of the {{Version nav}} template in the form of a dictionary.'''
    bracket_level = 0
    is_recording_version_nav = False
    this_parameter:str = None
    version_nav_parameters:list[str] = []
    for char_index, char in enumerate(wikitext):
        if char == "{":
            bracket_level += 1
        elif char == "}":
            bracket_level -= 1
            if bracket_level < 0: raise ValueError("Invalid brackets on \"%s\"!" % version.wiki_page)
            if is_recording_version_nav and bracket_level == 0:
                assert this_parameter.endswith("}")
                this_parameter = this_parameter[:-2]
                version_nav_parameters.append(this_parameter.lstrip("|"))
                break
        if bracket_level == 2 and wikitext[char_index:char_index + 11].strip().lower().replace("_", " ") == "version nav":
            is_recording_version_nav = True
        if char == "|" and is_recording_version_nav and bracket_level == 2:
            if this_parameter is not None:
                version_nav_parameters.append(this_parameter.lstrip("|"))
                this_parameter = ""
        if is_recording_version_nav:
            if this_parameter is None: this_parameter = ""
            this_parameter += char

    version_nav_data:dict[str,str] = {}
    if version_nav_parameters[0].lower().strip().replace("_", "") != "version nav":
        raise ValueError("Version nav parameters \"%s\" does not start with \"version nav\" on \"%s\"!" % (str(version_nav_parameters), version.wiki_page))
    version_nav_parameters.pop(0)
    for parameter in version_nav_parameters:
        key = parameter.split("=")[0].strip()
        value = "=".join(parameter.split("=")[1:]).strip()
        version_nav_data[key] = value
    if len(version_nav_data) == 0:
        raise RuntimeError("Something has gone wrong; version nav seems to be empty in \"%s\"!" % version.wiki_page)
    return version_nav_data

def split_by_multiple(string:str, seps:list[str]) -> list[str]:
    for sep in seps:
        new_string = seps[0].join(string.split(sep))
    return new_string.split(seps[0])

def parse_date(dates_string:str, version:Version.Version) -> list[str]:
    '''Verifies that the date(s) match the Version's date. Returns a list of warning messages.'''
    MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    warning_messages:list[str] = []
    dates_strings:list[str] = split_by_multiple(dates_string, ["<br>", "<br/>", "\n"])
    for split_dates_strings in dates_string.split("<br>"): dates_strings.extend(split_dates_strings.split("<br/>"))
    dates:list[datetime.date] = []
    for date_string in dates_strings:
        date_string_date = date_string.split("<")[0].split("{")[0].strip()
        if date_string_date.startswith(";") or date_string_date == "" or date_string_date.endswith("'''"): continue
        if " – " in date_string_date: # en-dash
            date_string_date = "–".join(date_string_date.split("–")[1:]).strip()
        elif " - " in date_string_date: # hyphen
            date_string_date = "-".join(date_string_date.split("-")[1:]).strip()
        elif ": " in date_string_date:
            date_string_date = ":".join(date_string_date.split(":")[1:]).strip()
        elif "''' " in date_string_date:
            date_string_date = "'''".join(date_string_date.split("'''")[2:]).strip()
        if date_string_date.count(" ") != 2:
            warning_messages.append("Date string \"%s\" on \"%s\" is not valid!" % (date_string_date, version.wiki_page))
            continue

        month_str, day_str, year_str = date_string_date.split(" ")
        if month_str not in MONTHS:
            warning_messages.append("Date string \"%s\" in \"%s\" has an invalid month in on \"%s\"!" % (date_string_date, version.name, version.wiki_page))
            continue
        if not day_str.endswith(","):
            warning_messages.append("Date string \"%s\"'s day \"%s\" does not end with a comma on \"%s\"!" % (date_string_date, day_str, version.wiki_page))
            continue
        if not day_str.replace(",", "").isdigit():
            warning_messages.append("Date string \"%s\" day \"%s\" is not a number on \"%s\"!" % (date_string_date, day_str, version.wiki_page))
            continue
        if not year_str.isdigit():
            warning_messages.append("Date string \"%s\" year \"%s\" is not a number on \"%s\"!" % (date_string_date, year_str, version.wiki_page))
            continue
        month = MONTHS[month_str]
        day = int(day_str.strip(","))
        year = int(year_str)
        date = datetime.date(year, month, day)
        dates.append(date)
    string_dates = str([str(date) for date in dates])
    if version.time not in dates and version.time is not None and len(dates) > 0:
        warning_messages.append("Version \"%s\"'s date \"%s\" does not match wiki page \"%s\"'s date(s) of \"%s\"" % (version.name, version.time, version.wiki_page, string_dates))
    elif version.time is None and len(dates) > 0:
        warning_messages.append("Version \"%s\" does not have a date, but could use date(s) \"%s\" from wiki page \"%s\"!" % (version.name, string_dates, version.wiki_page))
    elif version.time is not None and len(dates) == 0:
        warning_messages.append("Version \"%s\" (page \"%s\") does not have any valid dates!" % (version.name, version.wiki_page))
    return warning_messages

def parse_betas(version:Version.Version, mwapi:mediawikiapi.MediaWikiAPI) -> list[str]:
    '''Verifies information about the version's betas. Returns a list of warning messages.'''
    warning_messages:list[str] = []
    development_category_pages:list[mediawikiapi.WikipediaPage] = []
    assert version.development_category_names is not None
    for development_category_name in version.development_category_names:
        try:
            development_category_pages.append(mwapi.page(development_category_name, auto_suggest=False))
        except mediawikiapi.exceptions.PageError:
            pass
    wiki_betas:list[str] = []
    for development_category_page in development_category_pages:
        wiki_betas.extend(get_category_members(development_category_page))
    wiki_betas_set = set(wiki_betas)
    my_betas = set(child.wiki_page for child in version.children if child.ordering_tag is VersionTags.VersionTag.beta)
    if wiki_betas_set != my_betas:
        for my_beta in my_betas:
            if my_beta not in wiki_betas_set:
                warning_messages.append("Version \"%s\" (page \"%s\") lists a page \"%s\" as a beta that the wiki does not list as a beta!" % (version.name, version.wiki_page, my_beta))
        for wiki_beta in wiki_betas_set:
            if wiki_beta not in my_betas:
                warning_messages.append("Version \"%s\" (page \"%s\") does not list a page \"%s\" as a beta that the wiki does list as a beta!" % (version.name, version.wiki_page, wiki_beta))
    return warning_messages

def parse_client_downloads(client_dl_string:str, version:Version.Version) -> list[str]:
    '''Verifies information about the version's client download links. Returns a list of warning messages.'''
    warning_messages:list[str] = []
    links = [client_dl.split(" ")[0].split("]")[0] for client_dl in client_dl_string.strip().split("[")]
    links = [link for link in links if link != "" and "'''" not in link]
    for link in links:
        if not (link.startswith("http://") or link.startswith("https://")):
            warning_messages.append("Link \"%s\" on \"%s\" is invalid!" % (link, version.wiki_page))
    if version.download_method is Version.DownloadMethod.DOWNLOAD_URL:
        if version.download_link not in links:
            warning_messages.append("Link \"%s\" on \"%s\" is not in the page's links!" % (version.download_link, version.wiki_page))
    return warning_messages

def parse_main_list(versions:list[Version.Version], mwapi:mediawikiapi.MediaWikiAPI) -> list[str]:
    '''Compares Category:Bedrock Edition versions to the version list. Returns a list of warning messages.'''
    warning_messages:list[str] = []
    EXCEPTIONS = [
        "Bedrock Edition version history",
        "Bedrock Edition version history/Development versions",
        "Bedrock Edition 1.0.0", # redirect
        "Bedrock Edition 1.1.0", # redirect
        "Bedrock Edition 1.1.5", # redirect
        "Bedrock Edition 1.1.7", # redirect
        "Category:Pocket Edition versions",
        "Category:Bedrock Edition development versions by year",
        "Category:Bedrock Edition development versions by version",
        "Pocket Edition 1.10.0", # redirect
        "Pocket Edition 1.11.0", # redirect
        "Pocket Edition 1.12.0", # redirect
        "Pocket Edition 1.13.0", # redirect
        "Pocket Edition 1.14.0", # redirect
        "Pocket Edition 1.15.0", # redirect
        "Pocket Edition 1.16.0", # redirect
        "Pocket Edition 1.17.0", # redirect
        "Pocket Edition 1.2.0", # redirect
        "Pocket Edition 1.3.0", # redirect
        "Pocket Edition 1.4.0", # redirect
        "Pocket Edition 1.5.0", # redirect
        "Pocket Edition 1.6.0", # redirect
        "Pocket Edition 1.7.0", # redirect
        "Pocket Edition 1.8.0", # redirect
        "Pocket Edition 1.9.0", # redirect
        "Category:Pocket Edition development versions by version",
        "Category:Pocket Edition development versions by year",
    ]
    page_names = ["Category:Bedrock_Edition_versions", "Category:Pocket Edition versions"]
    wiki_versions:list[str] = []
    for page_name in page_names:
        page = mwapi.page(page_name, auto_suggest=False)
        wiki_versions.extend(get_category_members(page))
    for exception in EXCEPTIONS:
        if exception in wiki_versions: wiki_versions.remove(exception)
    my_versions = [version.wiki_page for version in versions]
    for my_version in my_versions:
        if my_version not in wiki_versions:
            warning_messages.append("My page \"%s\" does not exist on the wiki!" % (my_version))
    for wiki_version in wiki_versions:
        if wiki_version not in my_versions:
            warning_messages.append("Wiki page \"%s\" does not exist in the versions file!" % (wiki_version))
    return warning_messages

def validate(version:Version.Version, mwapi:mediawikiapi.MediaWikiAPI) -> list[str]:
    '''Prints a message if the wiki page of the version does not agree with the Version object.'''
    if version.wiki_page is None: raise ValueError("Wiki page of \"%s\" is None!" % version.name)
    page = mwapi.page(version.wiki_page, auto_suggest=False)
    wikitext = get_wikitext(page)
    infobox_data = get_infobox_data(wikitext, version)
    warning_messages:list[str] = []
    if "date" in infobox_data: warning_messages.extend(parse_date(infobox_data["date"], version))
    warning_messages.extend(parse_betas(version, mwapi))
    if "clientdl" in infobox_data: warning_messages.extend(parse_client_downloads(infobox_data["clientdl"], version))
    return warning_messages

def main() -> None:
    config = mediawikiapi.config.Config(mediawiki_url="http://minecraft.wiki/api.php")
    mwapi = mediawikiapi.MediaWikiAPI(config)
    versions = VersionsParser.versions.get()
    start_version = input("What version to start from? ")
    with open(FileManager.WIKI_VALIDATOR_WARNINGS_FILE, "wt") as f:
        f.write("")
    if start_version == "":
        scanning = True
    else: scanning = False
    versions_to_scan:list[Version.Version] = []
    for version in versions:
        if not scanning and version.name == start_version:
            scanning = True
        if scanning:
            versions_to_scan.append(version)
    if not scanning:
        print("No version found with name \"%s\"." % start_version)
    for version in versions_to_scan:
        print("Scanning \"%s\"..." % version.name)
        warnings = validate(version, mwapi)
        with open(FileManager.WIKI_VALIDATOR_WARNINGS_FILE, "at") as f:
            f.write("\n" + "\n".join(sorted(list(set(warnings)))))
