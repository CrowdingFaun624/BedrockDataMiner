import json
from typing import Any, Generator, Mapping, Sequence, TYPE_CHECKING, TypedDict, TypeVar

import Comparison.Comparer as Comparer
import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMiner as DataMiner
import Downloader.VersionsParser as VersionsParser
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import WaitValue

if TYPE_CHECKING:
    import Utilities.Version as Version

import DataMiners.BehaviorPacks.BehaviorPacksDataMiners as BehaviorPacksDataMiners
import DataMiners.BlocksClient.BlocksClientDataMiners as BlocksClientDataMiners
import DataMiners.Credits.CreditsDataMiners as CreditsDataMiners
import DataMiners.DuplicateSounds.DuplicateSoundsDataMiners as DuplicateSoundsDataMiners
import DataMiners.Entities.EntitiesDataMiners as EntitiesDataMiners
import DataMiners.EntitiesClient.EntitiesClientDataMiners as EntitiesClientDataMiners
import DataMiners.Items.ItemsDataMiners as ItemsDataMiners
import DataMiners.Languages.LanguagesDataMiners as LanguagesDataMiners
import DataMiners.LoadingTips.LoadingTipsDataMiners as LoadingTipsDataMiners
import DataMiners.LootTables.LootTablesDataMiners as LootTablesDataMiners
import DataMiners.Models.ModelsDataMiners as ModelsDataMiners
import DataMiners.MusicDefinitions.MusicDefinitionsDataMiners as MusicDefinitionsDataMiners
import DataMiners.NonExistentSounds.NonExistentSoundsDataMiners as NonExistentSoundsDataMiners
import DataMiners.Recipes.RecipesDataMiners as RecipesDataMiners
import DataMiners.ResourcePacks.ResourcePacksDataMiners as ResourcePacksDataMiners
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiners as SoundDefinitionsDataMiners
import DataMiners.SoundFiles.SoundFilesDataMiners as SoundFilesDataMiners
import DataMiners.SoundsJson.SoundsJsonDataMiners as SoundsJsonDataMiners
import DataMiners.Splashes.SplashesDataMiners as SplashesDataMiners
import DataMiners.TradeTables.TradeTablesDataMiners as TradeTablesDataMiners
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiners as UndefinedSoundEventsDataMiners
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiners as UnusedSoundEventsDataMiners

all_dataminers:Sequence[type[DataMiner.DataMiner]] = BehaviorPacksDataMiners.dataminers + BlocksClientDataMiners.dataminers + CreditsDataMiners.dataminers + DuplicateSoundsDataMiners.dataminers +\
    EntitiesDataMiners.dataminers + EntitiesClientDataMiners.dataminers + ItemsDataMiners.dataminers + LanguagesDataMiners.dataminers + LoadingTipsDataMiners.dataminers + LootTablesDataMiners.dataminers + MusicDefinitionsDataMiners.dataminers +\
    ModelsDataMiners.dataminers + NonExistentSoundsDataMiners.dataminers + RecipesDataMiners.dataminers + ResourcePacksDataMiners.dataminers + SoundDefinitionsDataMiners.dataminers +\
    SoundFilesDataMiners.dataminers + SoundsJsonDataMiners.dataminers + TradeTablesDataMiners.dataminers + SplashesDataMiners.dataminers + UndefinedSoundEventsDataMiners.dataminers +\
    UnusedSoundEventsDataMiners.dataminers

class DataMinerSettingsTypedDict(TypedDict):
    new: str|None
    old: str|None
    name: str|None
    dependencies: list[str]
    parameters: dict[str,Any]

class DataMinerCollectionTypedDict(TypedDict):
    file_name: str
    comparer: str
    dataminers: list[DataMinerSettingsTypedDict]

DataMinersCollections = dict[str,DataMinerCollectionTypedDict]

a = TypeVar("a")
def glue_adjacent(iter:list[a]) -> Generator[tuple[a, a], None, None]:
    if len(iter) == 0: return
    for i in range(0, len(iter) - 1, 2):
        yield iter[i], iter[i + 1]

class DataMinerCollectionIntermediate():

    def __init__(self, data:DataMinerCollectionTypedDict, name:str, comparers:dict[str,WaitValue[Comparer.Comparer]]) -> None:
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict!")
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        for key, key_type, key_type_str, is_required in (("file_name", str, "a str", True), ("comparer", str, "a str", True), ("dataminers", list, "a list", True)):
            if key not in data and is_required:
                raise KeyError("Required key \"%s\" is not in DataMinerCollection \"%s\"!" % (key, name))
            if key not in data: continue
            if not isinstance(data[key], key_type):
                raise TypeError("Key \"%s\" of DataMinerCollection \"%s\" is not %s, but instead %s!" % (key, name, key_type_str, data[key].__class__.__name__))
        if "dataminers" in data:
            for index, dataminer in enumerate(data["dataminers"]):
                if not isinstance(dataminer, dict):
                    raise TypeError("Dataminer %i of DataMinerCollection %s is not a dict!" % (index, name))
                for key, key_type, key_type_str, is_required in (
                    ("new", str|type(None), "a str or None", True), ("old", str|type(None), "a str or None", True),
                    ("name", str|None, "a str or None", True), ("dependencies", list, "a list", False), ("parameters", dict, "a dict", False)):
                        if key not in dataminer and is_required:
                            raise KeyError("Required key \"%s\" is not in DataMinerSettings %i of DataMinerCollection \"%s\"!" % (key, index, name))
                        if key not in dataminer: continue
                        if not isinstance(dataminer[key], key_type):
                            raise TypeError("Key \"%s\" of DataMinerSettings %i of DataMinerCollection \"%s\" is not %s, but instead %s!" % (key, index, name, key_type_str, dataminer[key].__class__.__name__))
                if "dependencies" in dataminer and not all(isinstance(item, str) for item in dataminer["dependencies"]):
                    raise TypeError("An item of key \"dependencies\" of DataMinerSettings %i of DataMinerCollection \"%s\" is not a str!" % (index, name))
        
        self.name = name
        self.file_name = data["file_name"]
        self.comparer_name = data["comparer"]
        self.dataminer_settings_strs = data["dataminers"]

        if self.comparer_name not in comparers:
            raise KeyError("Comparer \"%s\", referenced by DataMinerCollection \"%s\", does not exist!" % (self.comparer_name, self.name))
        self.comparer = comparers[self.comparer_name]
    
    def __repr__(self) -> str:
        return "<DataMinerCollectionIntermediate %s>" % self.name
    
    def create_final(self, all_dataminers:Mapping[str,type[DataMiner.DataMiner]]) -> DataMiner.DataMinerCollection:
        for index, dataminer_settings_str in enumerate(self.dataminer_settings_strs):
            if dataminer_settings_str["name"] is not None and dataminer_settings_str["name"] not in all_dataminers:
                raise KeyError("DataMiner \"%s\", referenced by DataMinerSettings %i of DataMinerCollection \"%s\", does not exist!" % (dataminer_settings_str["name"], index, self.name))
        dataminer_settings = [
            DataMiner.DataMinerSettings(
                start_version_str = dataminer_settings_str["old"],
                end_version_str = dataminer_settings_str["new"],
                dataminer_class = all_dataminers[dataminer_settings_str["name"]],
                dependencies = None if "dependencies" not in dataminer_settings_str else dataminer_settings_str["dependencies"],
                **{} if "parameters" not in dataminer_settings_str else dataminer_settings_str["parameters"],
            ) for dataminer_settings_str in self.dataminer_settings_strs
            if dataminer_settings_str["name"] is not None
        ]
        return DataMiner.DataMinerCollection(
            file_name = self.file_name,
            name = self.name,
            comparer = self.comparer,
            dataminers = dataminer_settings,
        )
    
    def check(self, intermediates:dict[str,"DataMinerCollectionIntermediate"], versions:dict[str,"Version.Version"]) -> list["Version.Version"]:
        used_versions:list["Version.Version"] = []
        for index, dataminer_settings in enumerate(self.dataminer_settings_strs):
            if "dependencies" not in dataminer_settings: continue
            for dependency in dataminer_settings["dependencies"]:
                if dependency not in intermediates:
                    raise KeyError("DataMinerSettings %i of DataMinerCollection \"%s\" references non-existent DataMinerCollection \"%s\"!" % (index, self.name, dependency))

            # ending DataMinerSettings must have null versions on corresponding versions; middle ones cannot be null.
            if index == 0:
                if dataminer_settings["new"] is not None:
                    raise ValueError("The new version of the first DataMinerSettings of DataMinerCollection \"%s\" is not None, but instead \"%s\"!" % (self.name, dataminer_settings["new"]))
            else:
                if dataminer_settings["new"] is None:
                    raise ValueError("The new version of DataMinerSettings %i of DataMinerCollection \"%s\" is None!" % (index, self.name))
                used_versions.append(versions[dataminer_settings["new"]])
            if index == len(self.dataminer_settings_strs) - 1:
                if dataminer_settings["old"] is not None:
                    raise ValueError("The old version of the last DataMinerSettings of DataMinerCollection \"%s\" is not None, but instead \"%s\"!" % (self.name, dataminer_settings["old"]))
            else:
                if dataminer_settings["old"] is None:
                    raise ValueError("The old version of DataMinerSettings %i of DataMinerCollection \"%s\" is None!" % (index, self.name))
                used_versions.append(versions[dataminer_settings["old"]])
        
        # checking that there are no gaps in the ranges by checking for equality
        for new_version, old_version in glue_adjacent(used_versions):
            if new_version != old_version:
                raise ValueError("DataMinerCollection \"%s\" has a gap between versions \"%s\" and \"%s\"!" % (self.name, new_version, old_version))
        
        return used_versions

def open_file() -> DataMinersCollections:
    with open(FileManager.DATAMINER_COLLECTIONS_FILE) as f:
        return json.load(f)

def load_dataminers() -> list[DataMiner.DataMinerCollection]:
    data = open_file()
    if not isinstance(data, dict):
        raise TypeError("dataminer_collections.json is not a dict!")
    
    comparers:dict[str,WaitValue[Comparer.Comparer]] = ComparerImporter.comparers
    all_dataminers_dict = {dataminer.__name__: dataminer for dataminer in all_dataminers}
    dataminer_collection_intermediates:dict[str,DataMinerCollectionIntermediate] = {}
    for name, dataminer_collection_data in data.items():
        dataminer_collection_intermediates[name] = DataMinerCollectionIntermediate(dataminer_collection_data, name, comparers)
    finals = [dataminer_collection_intermediate.create_final(all_dataminers_dict) for dataminer_collection_intermediate in dataminer_collection_intermediates.values()]
    versions = VersionsParser.versions_dict.get()
    all_used_versions:set["Version.Version"] = set()
    for dataminer_collection_intermediate in dataminer_collection_intermediates.values():
        used_versions = dataminer_collection_intermediate.check(dataminer_collection_intermediates, versions)
        all_used_versions.update(used_versions)
    return finals
