import json
import traceback
from typing import Any, Generator, Mapping, Sequence, TypedDict, TypeVar

import DataMiners.DataMiner as DataMiner
import Downloader.VersionsParser as VersionsParser
import Structure.StructureBase as StructureBase
import Structure.Importer.Importer as Importer
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import WaitValue
import Utilities.TypeVerifier as TypeVerifier
import Utilities.Version as Version

import DataMiners.BehaviorPacks.BehaviorPacksDataMiners as BehaviorPacksDataMiners
import DataMiners.BlocksClient.BlocksClientDataMiners as BlocksClientDataMiners
import DataMiners.DuplicateSounds.DuplicateSoundsDataMiners as DuplicateSoundsDataMiners
import DataMiners.GrabMultipleFiles.GrabMultipleFilesDataMiners as GrabMultipleFilesDataMiners
import DataMiners.GrabMultiplePackFiles.GrabMultiplePackFilesDataMiners as GrabMultiplePackFilesDataMiners
import DataMiners.GrabPackFile.GrabPackFileDataMiners as GrabPackFileDataMiners
import DataMiners.GrabSingleFile.GrabSingleFileDataMiners as GrabSingleFileDataMiners
import DataMiners.Items.ItemsDataMiners as ItemsDataMiners
import DataMiners.Language.LanguageDataMiners as LanguageDataMiners
import DataMiners.Languages.LanguagesDataMiners as LanguagesDataMiners
import DataMiners.Models.ModelsDataMiners as ModelsDataMiners
import DataMiners.MusicDefinitions.MusicDefinitionsDataMiners as MusicDefinitionsDataMiners
import DataMiners.NonExistentSounds.NonExistentSoundsDataMiners as NonExistentSoundsDataMiners
import DataMiners.ResourcePacks.ResourcePacksDataMiners as ResourcePacksDataMiners
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiners as SoundDefinitionsDataMiners
import DataMiners.SoundFiles.SoundFilesDataMiners as SoundFilesDataMiners
import DataMiners.SoundsJson.SoundsJsonDataMiners as SoundsJsonDataMiners
import DataMiners.Splashes.SplashesDataMiners as SplashesDataMiners
import DataMiners.TextureList.TextureListDataMiners as TextureListDataMiners
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiners as UndefinedSoundEventsDataMiners
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiners as UnusedSoundEventsDataMiners

all_dataminers:Sequence[type[DataMiner.DataMiner]] = []
dataminer_collections:list[Sequence[type[DataMiner.DataMiner]]] = [
    BehaviorPacksDataMiners.dataminers,
    BlocksClientDataMiners.dataminers,
    DuplicateSoundsDataMiners.dataminers,
    GrabMultipleFilesDataMiners.dataminers,
    GrabMultiplePackFilesDataMiners.dataminers,
    GrabPackFileDataMiners.dataminers,
    GrabSingleFileDataMiners.dataminers,
    ItemsDataMiners.dataminers,
    LanguageDataMiners.dataminers,
    LanguagesDataMiners.dataminers,
    ModelsDataMiners.dataminers,
    MusicDefinitionsDataMiners.dataminers,
    NonExistentSoundsDataMiners.dataminers,
    ResourcePacksDataMiners.dataminers,
    SoundDefinitionsDataMiners.dataminers,
    SoundFilesDataMiners.dataminers,
    SoundsJsonDataMiners.dataminers,
    SplashesDataMiners.dataminers,
    TextureListDataMiners.dataminers,
    UndefinedSoundEventsDataMiners.dataminers,
    UnusedSoundEventsDataMiners.dataminers
]
for dataminer_collection in dataminer_collections:
    all_dataminers.extend(dataminer_collection)

class DataMinerSettingsTypedDict(TypedDict):
    new: str|None
    old: str|None
    name: str|None
    dependencies: list[str]
    parameters: dict[str,Any]

class DataMinerCollectionTypedDict(TypedDict):
    file_name: str
    structure: str
    disabled: bool
    dataminers: list[DataMinerSettingsTypedDict]

DataMinersCollections = dict[str,DataMinerCollectionTypedDict]

a = TypeVar("a")
def glue_adjacent(iter:list[a]) -> Generator[tuple[a, a], None, None]:
    if len(iter) == 0: return
    for i in range(0, len(iter) - 1, 2):
        yield iter[i], iter[i + 1]

class DataMinerCollectionIntermediate():

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("structure", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("dataminers", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("new", "a str or None", True, (str, type(None))),
                TypeVerifier.TypedDictKeyTypeVerifier("old", "a str or None", True, (str, type(None))),
                TypeVerifier.TypedDictKeyTypeVerifier("name", "a str or None", True, (str, type(None))),
                TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
                TypeVerifier.TypedDictKeyTypeVerifier("parameters", "a dict", False, dict),
            ), list, "a dict", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("disabled", "a bool", False, bool)
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structures", "a dict", True, dict),
    )

    def __init__(self, data:DataMinerCollectionTypedDict, name:str, structures:dict[str,WaitValue[StructureBase.StructureBase]]) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "structures": structures})

        self.name = name
        self.file_name = data["file_name"]
        self.structure_name = data["structure"]
        self.dataminer_settings_strs = data["dataminers"]
        self.disabled = data["disabled"] if "disabled" in data else False

        if self.structure_name not in structures:
            raise KeyError("Structure \"%s\", referenced by DataMinerCollection \"%s\", does not exist!" % (self.structure_name, self.name))
        self.structure = structures[self.structure_name]
        self.dataminer_classes:dict[str,type[DataMiner.DataMiner]]|None = None

    def __repr__(self) -> str:
        return "<DataMinerCollectionIntermediate %s>" % self.name

    def create_final(self, all_dataminers:Mapping[str,type[DataMiner.DataMiner]]) -> DataMiner.DataMinerCollection:
        for index, dataminer_settings_str in enumerate(self.dataminer_settings_strs):
            if dataminer_settings_str["name"] is not None and dataminer_settings_str["name"] not in all_dataminers:
                raise KeyError("DataMiner \"%s\", referenced by DataMinerSettings %i of DataMinerCollection \"%s\", does not exist!" % (dataminer_settings_str["name"], index, self.name))
        self.dataminer_classes = {}
        dataminer_settings:list[DataMiner.DataMinerSettings] = []
        for dataminer_settings_str in self.dataminer_settings_strs:
            if dataminer_settings_str["name"] is None: continue
            dataminer_class = all_dataminers[dataminer_settings_str["name"]]
            self.dataminer_classes[dataminer_settings_str["name"]] = dataminer_class

            dataminer_settings.append(DataMiner.DataMinerSettings(
                start_version_str = dataminer_settings_str["old"],
                end_version_str = dataminer_settings_str["new"],
                dataminer_class = dataminer_class,
                name = self.name,
                dependencies = None if "dependencies" not in dataminer_settings_str else dataminer_settings_str["dependencies"],
                **{} if "parameters" not in dataminer_settings_str else dataminer_settings_str["parameters"],
            ))
        return DataMiner.DataMinerCollection(
            file_name = self.file_name,
            name = self.name,
            structure = self.structure,
            dataminers = dataminer_settings,
        )

    def check(self, intermediates:dict[str,"DataMinerCollectionIntermediate"], versions:dict[str,"Version.Version"]) -> list["Version.Version"]:
        # check parameters
        exceptions:list[Exception] = []
        for index, dataminer_settings in enumerate(self.dataminer_settings_strs):
            if "parameters" not in dataminer_settings: continue
            if dataminer_settings["name"] is None: continue
            if self.dataminer_classes is None: break
            dataminer_class = self.dataminer_classes[dataminer_settings["name"]]
            parameters = dataminer_class.parameters
            if parameters is not None:
                exceptions.extend(parameters.validate(dataminer_settings["parameters"]))
        for exception in exceptions:
            traceback.print_exception(exception)
            print()
        if len(exceptions) > 0:
            raise TypeError("Invalid parameters in DataMinerCollection \"%s\"!" % (self.name))

        # check dependencies
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

def get_dependencies(dataminer_settings:DataMiner.DataMinerSettings, dataminer_settings_dict:dict[str, DataMiner.DataMinerSettings], already:set[str]|None=None) -> list[str]:
    if already is None: already = set()
    assert dataminer_settings.name is not None
    if dataminer_settings.name in already:
        return [dataminer_settings.name]
    already.add(dataminer_settings.name)
    duplicated_dataminer_settings:list[str] = []
    for dependency in dataminer_settings.dependencies:
        already_copy = already.copy()
        duplicated_dataminer_settings.extend(get_dependencies(dataminer_settings_dict[dependency], dataminer_settings_dict, already_copy))
    return duplicated_dataminer_settings

def check_for_loops(used_versions:set[Version.Version], dataminers:list[DataMiner.DataMinerCollection]) -> None:
    '''Raises an error if a loop exists in any part.'''
    versions = sorted(used_versions)
    for version in versions:
        dataminer_settings_list = [dataminer.get_dataminer_settings(version) for dataminer in dataminers]
        if any(dataminer_settings.name is None for dataminer_settings in dataminer_settings_list):
            raise RuntimeError("A dataminer_settings has a None name!")
        dataminer_settings_dict = {dataminer_settings.name: dataminer_settings for dataminer_settings in dataminer_settings_list if dataminer_settings.name is not None}
        for dataminer_settings in dataminer_settings_list:
            duplicated_datminer_settings = get_dependencies(dataminer_settings, dataminer_settings_dict)
            if len(duplicated_datminer_settings) > 0:
                raise RuntimeError("Dataminer %s has a import loop containing [%s]!" % (dataminer_settings, ", ".join(duplicated_datminer_settings)))

def load_dataminers() -> list[DataMiner.DataMinerCollection]:
    data = open_file()
    if not isinstance(data, dict):
        raise TypeError("dataminer_collections.json is not a dict!")

    structures:dict[str,WaitValue[StructureBase.StructureBase]] = Importer.structures
    all_dataminers_dict = {dataminer.__name__: dataminer for dataminer in all_dataminers}
    dataminer_collection_intermediates:dict[str,DataMinerCollectionIntermediate] = {}
    for name, dataminer_collection_data in data.items():
        dataminer_collection_intermediates[name] = DataMinerCollectionIntermediate(dataminer_collection_data, name, structures)
    finals = [dataminer_collection_intermediate.create_final(all_dataminers_dict) for dataminer_collection_intermediate in dataminer_collection_intermediates.values() if not dataminer_collection_intermediate.disabled]
    versions = VersionsParser.versions_dict.get()
    all_used_versions:set["Version.Version"] = set()
    for dataminer_collection_intermediate in dataminer_collection_intermediates.values():
        used_versions = dataminer_collection_intermediate.check(dataminer_collection_intermediates, versions)
        all_used_versions.update(used_versions)
    check_for_loops(all_used_versions, finals)
    return finals
