import Component.Accessor.AccessorComponent as AccessorComponent
import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Component as Component
import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
import Component.DataMiner.DataMinerSettingsComponent as DataMinerSettingsComponent
import Component.Structure.BaseComponent as BaseComponent
import Component.Structure.CacheComponent as CacheComponent
import Component.Structure.DictComponent as DictComponent
import Component.Structure.GroupComponent as GroupComponent
import Component.Structure.KeymapComponent as KeymapComponent
import Component.Structure.ListComponent as ListComponent
import Component.Structure.NbtBaseComponent as NbtBaseComponent
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.PrimitiveComponent as PrimitiveComponent
import Component.Structure.SetComponent as SetComponent
import Component.Structure.StringComponent as StringComponent
import Component.Structure.TagComponent as TagComponent
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Component.Structure.VolumeComponent as VolumeComponent
import Component.Version.VersionComponent as VersionComponent
import Component.Version.VersionFileComponent as VersionFileComponent
import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent
import Component.VersionTag.LatestSlotComponent as LatestSlotComponent
import Component.VersionTag.RangeVersionTagAutoAssignerComponent as RangeVersionTagAutoAssignerComponent
import Component.VersionTag.VersionTagComponent as VersionTagComponent
import Component.VersionTag.VersionTagOrderComponent as VersionTagOrderComponent

component_types:list[type[Component.Component]] = [
    AccessorComponent.AccessorComponent,
    AccessorTypeComponent.AccessorTypeComponent,
    BaseComponent.BaseComponent,
    CacheComponent.CacheComponent,
    DataMinerCollectionComponent.DataMinerCollectionComponent,
    DataMinerSettingsComponent.DataMinerSettingsComponent,
    DictComponent.DictComponent,
    GroupComponent.GroupComponent,
    KeymapComponent.KeymapComponent,
    LatestSlotComponent.LatestSlotComponent,
    ListComponent.ListComponent,
    NbtBaseComponent.NbtBaseComponent,
    NormalizerComponent.NormalizerComponent,
    PrimitiveComponent.PrimitiveComponent,
    SetComponent.SetComponent,
    StringComponent.StringComponent,
    RangeVersionTagAutoAssignerComponent.RangeVersionTagAutoAssignerComponent,
    TagComponent.TagComponent,
    TypeAliasComponent.TypeAliasComponent,
    VersionComponent.VersionComponent,
    VersionFileComponent.VersionFileComponent,
    VersionFileTypeComponent.VersionFileTypeComponent,
    VersionTagComponent.VersionTagComponent,
    VersionTagOrderComponent.VersionTagOrderComponent,
    VolumeComponent.VolumeComponent,
]
