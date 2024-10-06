import re
from typing import cast

import Component.Importer as Importer
import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.FileManager as FileManager
import Version.Version as Version


def do_dataminer_collection(
    dataminer_collection:DataMinerCollection.DataMinerCollection  ,
    version:Version.Version,
    dependencies:DataMinerEnvironment.DataMinerDependencies,
    file_set:FileDataMiner.FileSet,
    version_files_covered:set[str],
    version_files_covered_dict:dict[DataMiner.DataMiner,set[str]],
) -> None:
    dataminer_settings = dataminer_collection.get_dataminer_settings(version)
    dataminer_class = dataminer_settings.get_dataminer_class()
    if not issubclass(dataminer_class, FileDataMiner.FileDataMiner):
        return
    dataminer = dataminer_class(version, dataminer_settings)
    for dependency_dataminer_collection in dataminer_settings.get_dependencies():
        if dependencies.has_item(dependency_dataminer_collection.name): continue
        dependency_dataminer_settings = dependency_dataminer_collection.get_dataminer_settings(version)
        dependency_dataminer_class = dependency_dataminer_settings.get_dataminer_class()
        if issubclass(dependency_dataminer_class, DataMiner.NullDataMiner):
            raise ValueError("%r has a NullDataMiner dependency %r for %r!" % (dataminer, dependency_dataminer_settings, version))
        dependency_dataminer = dependency_dataminer_class(version, dependency_dataminer_settings)
        if isinstance(dependency_dataminer, FileDataMiner.FileDataMiner):
            raise ValueError("%r has a FileDataMiner dependency (%r) in %r, which is not supported!" % (dataminer, dependency_dataminer, version))
        dependencies.set_item(dependency_dataminer.name, dependency_dataminer.get_data_file())
    environment = DataMinerEnvironment.DataMinerEnvironment(dependencies, StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining))
    dataminer_files_covered = dataminer.get_coverage(file_set, environment)
    if len(overlapping_files := version_files_covered.intersection(dataminer_files_covered)) > 0:
        other_dataminers = [
            other_dataminer
            for other_dataminer, other_dataminer_coverage in version_files_covered_dict.items()
            if len(other_dataminer_coverage.intersection(dataminer_files_covered)) > 0
        ]
        raise RuntimeError("The following files in %r are covered by %r and dataminers [%s]: [%s]" % (version, dataminer, ", ".join(repr(other_dataminer) for other_dataminer in other_dataminers), ", ".join(overlapping_files)))
    version_files_covered.update(dataminer_files_covered)
    version_files_covered_dict[dataminer] = dataminer_files_covered

def get_file_name(version:Version.Version, index:int) -> str:
    return "%s %s.txt" % (str(index).zfill(4), version.name)

def do_version(version:Version.Version, all_files_dataminer:DataMinerCollection.DataMinerCollection, version_index:int, total_versions:int, dataminer_collections:dict[str,DataMinerCollection.DataMinerCollection]) -> None:
    if not all_files_dataminer.supports_version(version):
        print("Skipped coverage report of %r (%i/%i) due to not supporting %r." % (version, version_index, total_versions, all_files_dataminer))
        return
    print("Starting coverage report of %r (%i/%i)" % (version, version_index, total_versions))
    file_set_list:dict[str,str] = all_files_dataminer.get_data_file(version)
    file_set_set = set(file_set_list)
    file_set = FileDataMiner.FileSet(file_set_list)
    version_files_covered:set[str] = set()
    version_files_covered_dict:dict[DataMiner.DataMiner,set[str]] = {}
    dependencies = DataMinerEnvironment.DataMinerDependencies({})
    for dataminer_collection in dataminer_collections.values():
        do_dataminer_collection(dataminer_collection, version, dependencies, file_set, version_files_covered, version_files_covered_dict)
    leftover_files = file_set_set - version_files_covered
    with open(FileManager.OUTPUT_DIRECTORY.joinpath(get_file_name(version, version_index)), "wt") as f:
        f.write("\n".join(sorted(leftover_files)))

def pick_version(versions:dict[str,Version.Version]) -> tuple[Version.Version, int]:
    while True:
        user_input = input("Which version name? ")
        if user_input in versions:
            version = versions[user_input]
            break
        else: continue
    version_index = len(versions) - version.index - 1
    return version, version_index

def do_all() -> None:
    for file in FileManager.OUTPUT_DIRECTORY.iterdir():
        if not file.is_file(): continue
        file.unlink()
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    for version_index, version in enumerate(reversed(versions.values())):
        do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)
    print("Finished all coverage reports")

def do_all_that_contain() -> None:
    search_term = input("Search term: ")
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    for version_index, version in enumerate(reversed(versions.values())):
        file_path = FileManager.OUTPUT_DIRECTORY.joinpath(get_file_name(version, version_index))
        if not file_path.exists():
            continue
        with open(file_path, "rt") as f:
            contents = f.readlines()
        if any(search_term in content for content in contents):
            do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)
    print("Finished all coverage reports")

def do_one() -> None:
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    version, version_index = pick_version(versions)
    do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)

def do_before() -> None:
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    target_version, target_version_index = pick_version(versions)
    for version_index, version in enumerate(reversed(versions.values())):
        if version_index < target_version_index: continue
        do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)

def search() -> None:
    search_term = input("Search term: ")
    for file in FileManager.OUTPUT_DIRECTORY.iterdir():
        if not file.is_file(): continue
        with open(file, "rt") as f:
            contents = f.readlines()
        count = 0
        usage = ""
        for content in contents:
            if search_term in content:
                count += 1
                usage = content.rstrip()
        if count == 0:
            pass
        elif count == 1:
            print(file.stem, count, usage)
        else:
            print(file.stem, count)

REMOVE_FILES = {
    "animation/DialogAnimation.xml",
    "animation/ScreenAnimation.xml",
    "apkprotector_dex/classes-v1.bin", # idk how these work.
    "apkprotector_dex/classes-v2.bin",
    "behavior_packs/agent_gametest/.prettierrc.json",
    "behavior_packs/vanilla_1.19.60/wandering_trader_trades.json",
    "behavior_packs/vanilla_1.19.60/tropicalfish.json",
    "behavior_packs/vanilla_1.20.10/donkey.json", # useless files that are completely useless
    "behavior_packs/vanilla_1.20.10/horse.json",
    "behavior_packs/vanilla_1.20.10/llama.json",
    "behavior_packs/vanilla_1.20.10/mule.json",
    "behavior_packs/vanilla_1.20.10/trader_llama.json",
    "behavior_packs/vanilla_edu_gametest/.prettierrc.json",
    "behavior_packs/vanilla_gametest/.prettierrc.json", # these aren't used by the game.
    "behavior_packs/vanilla_gametest/.vscode/extensions.json",
    "behavior_packs/vanilla_gametest/.vscode/settings.json",
    "behavior_packs/vanilla_gametest/gametests/BlockTests.js", # only exist in 1.16.210.60-1.16.210
    "behavior_packs/vanilla_gametest/gametests/DoorTests.js",
    "behavior_packs/vanilla_gametest/gametests/MinecartTests.js",
    "crush.bat", # appears to run "pngcrush.exe" on all png files.
    "DoSoundStuff.bat", # bat file that uses the fsb program to turn OGGs into FSBs. Only exists in a0.12.1_build13 and a0.12.1
    "Empty.txt", # literally an empty file.
    "font/glyph_sizes.bin", # identical to images/font/glyph_sizes.bin in all versions where both exist.
    "lang/make_es_419.py", # random utility python file; is not used by Bedrock engine.
    "lang/README.md", # very short md file that does not appear to change.
    "loc/make_es_419.py",
    "loc/README.md",
    "resourcepacks/education/skinpacks/skinpacks.json",
    "resourcepacks/fantasy/entities.list",
    "resource_packs/festivemashup2016/textures/missing.txt", # exists only in a0.17.0.2. Likely contains files that are referenced by the pack but aren't present in the textures directory
    "resource_packs/festivemashup2016/textures/typeMismatch.txt", # exists only in a0.17.0.2. Lists file names that have the same path and name but different suffixes.
    "resourcepacks/natural/entities.list",
    "resource_packs/skins/skinpacks/FestiveMashup2016/SkinRepository_CPP.txt",
    "resource_packs/skins/skinpacks/MagicTheGathering/SkinRepository_CPP.txt", # exists 1.0.6.0 - 1.1.7; contains c++ code listing skin names and their geometries and file paths
    "resourcepacks/skins/skinpacks/skinpacks.json", # only exists during a0.16.0_build3
    "resourcepacks/vanilla/client/texts/ja_JP/pack_manifest.json",
    "resourcepacks/vanilla/client/texts/ja_JP/resources.json",
    "resourcepacks/vanilla/client/texts/zh_TW/resources.json",
    "resourcepacks/vanilla/components.txt", # basically an entity component tutorial. Only exists for a0.16.0_build1 and a0.16.0_build4
    "resourcepacks/vanilla/entities.list", # just a plaintext list of all of the files in the entities/ directory of the vanilla resource pack
    "resource_packs/vanilla/font/NotoSans/LICENSE_OFL.txt", # I don't care.
    "resource_packs/vanilla/font/NotoSans/README",
    "resourcepacks/vanilla/loc/ja_JP/pack_manifest.json",
    "resourcepacks/vanilla/loc/ja_JP/resources.json",
    "resourcepacks/vanilla/loc/zh_TW/resources.json",
    "resourcepacks/vanilla/server/entities.list",
    "resourcepacks/vanilla/texts/ja_JP/pack_manifest.json", # language file that does not change
    "resourcepacks/vanilla/texts/ja_JP/resources.json", # language file that does not change
    "resourcepacks/vanilla/texts/zh_TW/resources.json", # language file that does not change
    "resource_packs/vanilla/ui/play_screen.json.bak", # .bak stands for backup. Isn't actually used.
    "resource_packs/vanilla_1.18.0/loot_tables/chests/simple_dungeon.json", # based on https://bugs.mojang.com/browse/MCPE-146264, seems to be unused
    "store_cache.zip",
    "test/assets/ScriptServerTests/scripts/script-server-test-010.js", # exists for 1.19.70-1.19.73
    "test/assets/ScriptServerTests/scripts/script-server-test-latest.js",
    "test/MPThresholds.json", # only exists in IPAs 1.13.2 and 1.13.3.
    "world_templates/festivemashup2016.mctemplate",
}

REMOVE_REGEX = [re.compile(pattern) for pattern in [
    r"[a-zA-Z0-9]{20}\/[a-zA-Z0-9]{15}", # also known as apkprotector_dex/classes-v1.bin and apkprotector_dex/classes-v2.bin. super inconsistent files, keep appearing and disappearing. Plus idk how they work.
]]

REMOVE_PREFIXES = [
    "levels/a/chunk_", # level data files that do not change once during their lifetime.
]

REMOVE_SUFFIXES = [
    ".brarchive", # binary files that exclusively restate what's in other files
    ".fontdata", # relating to "smooth" font files.
    ".zipe", # encrypted zip file of skin textures. Decryption method is not known.
    ".gitignore", # are not used by the game
]

def do_compare() -> None:
    comparison_folder = FileManager.OUTPUT_DIRECTORY.joinpath("comparison")
    comparison_folder.mkdir(exist_ok=True)
    for file in comparison_folder.iterdir():
        file.unlink()
    previous_file = "none"
    previous:list[str] = []
    previous_set:set[str] = set()
    for index, file in enumerate(reversed(list(FileManager.OUTPUT_DIRECTORY.iterdir()))):
        if not file.is_file(): continue
        with open(file, "rt") as f:
            current_set = set(item.rstrip() for item in f.readlines())
            current_set -= REMOVE_FILES
            current_set = {item for item in current_set if not any(item.endswith(suffix) for suffix in REMOVE_SUFFIXES) and not any(item.startswith(prefix) for prefix in REMOVE_PREFIXES)}
            current_set = {item for item in current_set if not any(pattern.fullmatch(item) for pattern in REMOVE_REGEX)}
            current = list(current_set)
        additions:list[str] = [current_item for current_item in current if current_item not in previous_set]
        removals:list[str] = [previous_item for previous_item in previous if previous_item not in current_set]
        if len(additions) > 0 or len(removals) > 0:
            with open(comparison_folder.joinpath("report_%s.txt" % (str(index).zfill(4),)), "wt") as f:
                report = "Comparison between %s and %s\n\n" % (previous_file, file.name)
                report += "Additions:\n%s\n\n" % ("\n".join(sorted(additions)))
                report += "Removals:\n%s\n\n" % ("\n".join(sorted(removals)))
                f.write(report)
        previous = current
        previous_set = current_set
        previous_file = file.name

def main() -> None:
    functions = {
        "all": do_all,
        "all_that_contain": do_all_that_contain,
        "before": do_before,
        "compare": do_compare,
        "one": do_one,
        "search": search
    }
    user_input = None
    while user_input not in functions:
        user_input = input("Choose from [%s]: " % (", ".join(functions.keys())))
    functions[user_input]()
