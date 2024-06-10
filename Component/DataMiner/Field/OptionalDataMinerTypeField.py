from typing import Sequence

import Component.Field.Field as Field
import DataMiners.AllFiles.AllFilesDataMiners as AllFilesDataMiners
import DataMiners.BehaviorPacks.BehaviorPacksDataMiners as BehaviorPacksDataMiners
import DataMiners.BlocksClient.BlocksClientDataMiners as BlocksClientDataMiners
import DataMiners.DataMiner as DataMiner
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
import DataMiners.TagSearcher.TagSearcherDataMiners as TagSearcherDataMiners
import DataMiners.TextureList.TextureListDataMiners as TextureListDataMiners
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiners as UndefinedSoundEventsDataMiners
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiners as UnusedSoundEventsDataMiners

all_dataminers:dict[str, type[DataMiner.DataMiner]] = {}
dataminer_collections:list[Sequence[type[DataMiner.DataMiner]]] = [
    AllFilesDataMiners.dataminers,
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
    TagSearcherDataMiners.dataminers,
    TextureListDataMiners.dataminers,
    UndefinedSoundEventsDataMiners.dataminers,
    UnusedSoundEventsDataMiners.dataminers,
]
for dataminer_collection in dataminer_collections:
    all_dataminers.update({dataminer.__name__: dataminer for dataminer in dataminer_collection})

class OptionalDataMinerTypeField(Field.Field):
    
    def __init__(self, dataminer_name:str|None, path: list[str | int]) -> None:
        '''
        :dataminer_name: The name of the DataMiner referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.dataminer = all_dataminers[dataminer_name] if dataminer_name is not None else DataMiner.NullDataMiner
    
    def get_final(self) -> type[DataMiner.DataMiner]|type[DataMiner.NullDataMiner]:
        return self.dataminer

    def exists(self) -> bool:
        "Returns True if this Field was initialized with a str, and False if it was initialized with None"
        return self.dataminer is not DataMiner.NullDataMiner
