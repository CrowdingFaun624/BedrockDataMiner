from typing import Sequence

import Component.Field.Field as Field
import DataMiner.AllFiles.AllFilesDataMiners as AllFilesDataMiners
import DataMiner.BehaviorPacks.BehaviorPacksDataMiners as BehaviorPacksDataMiners
import DataMiner.BlocksClient.BlocksClientDataMiners as BlocksClientDataMiners
import DataMiner.DataMiner as DataMiner
import DataMiner.DuplicateSounds.DuplicateSoundsDataMiners as DuplicateSoundsDataMiners
import DataMiner.GrabMultipleFiles.GrabMultipleFilesDataMiners as GrabMultipleFilesDataMiners
import DataMiner.GrabMultiplePackFiles.GrabMultiplePackFilesDataMiners as GrabMultiplePackFilesDataMiners
import DataMiner.GrabPackFile.GrabPackFileDataMiners as GrabPackFileDataMiners
import DataMiner.GrabSingleFile.GrabSingleFileDataMiners as GrabSingleFileDataMiners
import DataMiner.Items.ItemsDataMiners as ItemsDataMiners
import DataMiner.Language.LanguageDataMiners as LanguageDataMiners
import DataMiner.Languages.LanguagesDataMiners as LanguagesDataMiners
import DataMiner.Models.ModelsDataMiners as ModelsDataMiners
import DataMiner.MusicDefinitions.MusicDefinitionsDataMiners as MusicDefinitionsDataMiners
import DataMiner.NonExistentSounds.NonExistentSoundsDataMiners as NonExistentSoundsDataMiners
import DataMiner.ResourcePacks.ResourcePacksDataMiners as ResourcePacksDataMiners
import DataMiner.SoundDefinitions.SoundDefinitionsDataMiners as SoundDefinitionsDataMiners
import DataMiner.SoundFiles.SoundFilesDataMiners as SoundFilesDataMiners
import DataMiner.SoundsJson.SoundsJsonDataMiners as SoundsJsonDataMiners
import DataMiner.Splashes.SplashesDataMiners as SplashesDataMiners
import DataMiner.TagSearcher.TagSearcherDataMiners as TagSearcherDataMiners
import DataMiner.TextureList.TextureListDataMiners as TextureListDataMiners
import DataMiner.UndefinedSoundEvents.UndefinedSoundEventsDataMiners as UndefinedSoundEventsDataMiners
import DataMiner.UnusedSoundEvents.UnusedSoundEventsDataMiners as UnusedSoundEventsDataMiners

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
