import Component.Accessor.AccessorComponent as AccessorComponent
import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Component as Component
import Component.Dataminer.CoverageDataminerCollectionComponent as CoverageDataminerCollectionComponent
import Component.Dataminer.DataminerCollectionComponent as DataminerCollectionComponent
import Component.Dataminer.DataminerSettingsComponent as DataminerSettingsComponent
import Component.Log.LogComponent as LogComponent
import Component.Serializer.SerializerComponent as SerializerComponent
import Component.Structure.BaseComponent as BaseComponent
import Component.Structure.CacheComponent as CacheComponent
import Component.Structure.DictComponent as DictComponent
import Component.Structure.FileComponent as FileComponent
import Component.Structure.KeymapComponent as KeymapComponent
import Component.Structure.ListComponent as ListComponent
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.PrimitiveComponent as PrimitiveComponent
import Component.Structure.SequenceComponent as SequenceComponent
import Component.Structure.SetComponent as SetComponent
import Component.Structure.StringComponent as StringComponent
import Component.Structure.StructureTagComponent as StructureTagComponent
import Component.Structure.SwitchComponent as SwitchComponent
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Component.Structure.UnionComponent as UnionComponent
import Component.Tablifier.TablifierComponent as TablifierComponent
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
    CoverageDataminerCollectionComponent.CoverageDataminerCollectionComponent,
    DataminerCollectionComponent.DataminerCollectionComponent,
    DataminerSettingsComponent.DataminerSettingsComponent,
    DictComponent.DictComponent,
    FileComponent.FileComponent,
    KeymapComponent.KeymapComponent,
    LatestSlotComponent.LatestSlotComponent,
    ListComponent.ListComponent,
    LogComponent.LogComponent,
    NormalizerComponent.NormalizerComponent,
    PrimitiveComponent.PrimitiveComponent,
    SerializerComponent.SerializerComponent,
    SequenceComponent.SequenceComponent,
    SetComponent.SetComponent,
    StringComponent.StringComponent,
    RangeVersionTagAutoAssignerComponent.RangeVersionTagAutoAssignerComponent,
    StructureTagComponent.StructureTagComponent,
    SwitchComponent.SwitchComponent,
    TablifierComponent.TablifierComponent,
    TypeAliasComponent.TypeAliasComponent,
    UnionComponent.UnionComponent,
    VersionComponent.VersionComponent,
    VersionFileComponent.VersionFileComponent,
    VersionFileTypeComponent.VersionFileTypeComponent,
    VersionTagComponent.VersionTagComponent,
    VersionTagOrderComponent.VersionTagOrderComponent,
]
