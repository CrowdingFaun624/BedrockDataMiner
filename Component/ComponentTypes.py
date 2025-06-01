import Component.Accessor.AccessorComponent as AccessorComponent
import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Component as Component
import Component.Dataminer.CoverageDataminerCollectionComponent as CoverageDataminerCollectionComponent
import Component.Dataminer.DataminerCollectionComponent as DataminerCollectionComponent
import Component.Dataminer.DataminerSettingsComponent as DataminerSettingsComponent
import Component.Log.LogComponent as LogComponent
import Component.Serializer.SerializerComponent as SerializerComponent
import Component.Structure.CacheStructureComponent as CacheStructureComponent
import Component.Structure.ConditionStructureComponent as ConditionStructureComponent
import Component.Structure.DictStructureComponent as DictStructureComponent
import Component.Structure.FileStructureComponent as FileStructureComponent
import Component.Structure.FilterComponent as FilterComponent
import Component.Structure.KeymapStructureComponent as KeymapStructureComponent
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.NumberStructureComponent as NumberStructureComponent
import Component.Structure.PrimitiveStructureComponent as PrimitiveStructureComponent
import Component.Structure.SequenceStructureComponent as SequenceStructureComponent
import Component.Structure.StringStructureComponent as StringStructureComponent
import Component.Structure.StructureBaseComponent as StructureBaseComponent
import Component.Structure.StructureTagComponent as StructureTagComponent
import Component.Structure.SwitchStructureComponent as SwitchStructureComponent
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Component.Structure.UnionStructureComponent as UnionStructureComponent
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
    CacheStructureComponent.CacheStructureComponent,
    ConditionStructureComponent.ConditionStructureComponent,
    CoverageDataminerCollectionComponent.CoverageDataminerCollectionComponent,
    DataminerCollectionComponent.DataminerCollectionComponent,
    DataminerSettingsComponent.DataminerSettingsComponent,
    DictStructureComponent.DictStructureComponent,
    FileStructureComponent.FileStructureComponent,
    FilterComponent.AndFilterComponent,
    FilterComponent.EqFilterComponent,
    FilterComponent.GeFilterComponent,
    FilterComponent.GtFilterComponent,
    FilterComponent.KeyNotPresentFilterComponent,
    FilterComponent.KeyPresentFilterComponent,
    FilterComponent.LeFilterComponent,
    FilterComponent.LtFilterComponent,
    FilterComponent.NandFilterComponent,
    FilterComponent.NeFilterComponent,
    FilterComponent.NorFilterComponent,
    FilterComponent.OrFilterComponent,
    KeymapStructureComponent.KeymapStructureComponent,
    LatestSlotComponent.LatestSlotComponent,
    LogComponent.LogComponent,
    NormalizerComponent.NormalizerComponent,
    NumberStructureComponent.NumberStructureComponent,
    PrimitiveStructureComponent.PrimitiveStructureComponent,
    SequenceStructureComponent.SequenceStructureComponent,
    SerializerComponent.SerializerComponent,
    StringStructureComponent.StringStructureComponent,
    RangeVersionTagAutoAssignerComponent.RangeVersionTagAutoAssignerComponent,
    StructureBaseComponent.StructureBaseComponent,
    StructureTagComponent.StructureTagComponent,
    SwitchStructureComponent.SwitchStructureComponent,
    TablifierComponent.TablifierComponent,
    TypeAliasComponent.TypeAliasComponent,
    UnionStructureComponent.UnionStructureComponent,
    VersionComponent.VersionComponent,
    VersionFileComponent.VersionFileComponent,
    VersionFileTypeComponent.VersionFileTypeComponent,
    VersionTagComponent.VersionTagComponent,
    VersionTagOrderComponent.VersionTagOrderComponent,
]
