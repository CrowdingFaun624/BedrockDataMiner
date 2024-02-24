import DataMiners.BehaviorPacks.BehaviorPacksComparer as BehaviorPacksComparer
import DataMiners.BlocksClient.BlocksClientComparer as BlocksClientComparer
import DataMiners.Credits.CreditsComparer as CreditsComparer
import DataMiners.DuplicateSounds.DuplicateSoundsComparer as DuplicateSoundsComparer
import DataMiners.Entities.EntitiesComparer as EntitiesComparer
import DataMiners.Items.ItemsComparer as ItemsComparer
import DataMiners.Languages.LanguagesComparer as LanguagesComparer
import DataMiners.LootTables.LootTablesComparer as LootTablesComparer
import DataMiners.MusicDefinitions.MusicDefinitionsComparer as MusicDefinitionsComparer
import DataMiners.NonExistentSounds.NonExistentSoundsComparer as NonExistentSoundsComparer
import DataMiners.Recipes.RecipesComparer as RecipesComparer
import DataMiners.ResourcePacks.ResourcePacksComparer as ResourcePacksComparer
import DataMiners.SoundDefinitions.SoundDefinitionsComparer as SoundDefinitionsComparer
import DataMiners.SoundFiles.SoundFilesComparer as SoundFilesComparer
import DataMiners.SoundsJson.SoundsJsonComparer as SoundsJsonComparer
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsComparer as UndefinedSoundEventsComparer
import DataMiners.UnusedSoundEvents.UnusedSoundEventsComparer as UnusedSoundEventsComparer

comparers = {
    "behavior_packs":         BehaviorPacksComparer.comparer,
    "blocks_client":          BlocksClientComparer.comparer,
    "credits":                CreditsComparer.comparer,
    "duplicate_sounds":       DuplicateSoundsComparer.comparer,
    "entities":               EntitiesComparer.comparer,
    "items":                  ItemsComparer.comparer,
    "languages":              LanguagesComparer.comparer,
    "loot_tables":            LootTablesComparer.comparer,
    "music_definitions":      MusicDefinitionsComparer.comparer,
    "non_existent_sounds":    NonExistentSoundsComparer.comparer,
    "recipes":                RecipesComparer.comparer,
    "resource_packs":         ResourcePacksComparer.comparer,
    "sound_definitions":      SoundDefinitionsComparer.comparer,
    "sound_files":            SoundFilesComparer.comparer,
    "sounds_json":            SoundsJsonComparer.comparer,
    "undefined_sound_events": UndefinedSoundEventsComparer.comparer,
    "unused_sound_events":    UnusedSoundEventsComparer.comparer,
}
