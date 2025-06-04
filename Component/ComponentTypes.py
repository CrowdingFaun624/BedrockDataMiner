from Component.Accessor.AccessorComponent import AccessorComponent
from Component.Accessor.AccessorTypeComponent import AccessorTypeComponent
from Component.Component import Component
from Component.Dataminer.CoverageDataminerCollectionComponent import (
    CoverageDataminerCollectionComponent,
)
from Component.Dataminer.DataminerCollectionComponent import (
    DataminerCollectionComponent,
)
from Component.Dataminer.DataminerSettingsComponent import DataminerSettingsComponent
from Component.Log.LogComponent import LogComponent
from Component.Serializer.SerializerComponent import SerializerComponent
from Component.Structure.CacheStructureComponent import CacheStructureComponent
from Component.Structure.ConditionStructureComponent import ConditionStructureComponent
from Component.Structure.DictStructureComponent import DictStructureComponent
from Component.Structure.FileStructureComponent import FileStructureComponent
from Component.Structure.FilterComponent import (
    AndFilterComponent,
    EqFilterComponent,
    GeFilterComponent,
    GtFilterComponent,
    KeyNotPresentFilterComponent,
    KeyPresentFilterComponent,
    LeFilterComponent,
    LtFilterComponent,
    NandFilterComponent,
    NeFilterComponent,
    NorFilterComponent,
    OrFilterComponent,
)
from Component.Structure.KeymapStructureComponent import KeymapStructureComponent
from Component.Structure.NormalizerComponent import NormalizerComponent
from Component.Structure.NumberStructureComponent import NumberStructureComponent
from Component.Structure.PrimitiveStructureComponent import PrimitiveStructureComponent
from Component.Structure.SequenceStructureComponent import SequenceStructureComponent
from Component.Structure.StringStructureComponent import StringStructureComponent
from Component.Structure.StructureBaseComponent import StructureBaseComponent
from Component.Structure.StructureTagComponent import StructureTagComponent
from Component.Structure.SwitchStructureComponent import SwitchStructureComponent
from Component.Structure.TypeAliasComponent import TypeAliasComponent
from Component.Structure.UnionStructureComponent import UnionStructureComponent
from Component.Tablifier.TablifierComponent import TablifierComponent
from Component.Version.VersionComponent import VersionComponent
from Component.Version.VersionFileComponent import VersionFileComponent
from Component.Version.VersionFileTypeComponent import VersionFileTypeComponent
from Component.VersionTag.LatestSlotComponent import LatestSlotComponent
from Component.VersionTag.RangeVersionTagAutoAssignerComponent import (
    RangeVersionTagAutoAssignerComponent,
)
from Component.VersionTag.VersionTagComponent import VersionTagComponent
from Component.VersionTag.VersionTagOrderComponent import VersionTagOrderComponent

component_types:list[type[Component]] = [
    AccessorComponent,
    AccessorTypeComponent,
    CacheStructureComponent,
    ConditionStructureComponent,
    CoverageDataminerCollectionComponent,
    DataminerCollectionComponent,
    DataminerSettingsComponent,
    DictStructureComponent,
    FileStructureComponent,
    AndFilterComponent,
    EqFilterComponent,
    GeFilterComponent,
    GtFilterComponent,
    KeyNotPresentFilterComponent,
    KeyPresentFilterComponent,
    LeFilterComponent,
    LtFilterComponent,
    NandFilterComponent,
    NeFilterComponent,
    NorFilterComponent,
    OrFilterComponent,
    KeymapStructureComponent,
    LatestSlotComponent,
    LogComponent,
    NormalizerComponent,
    NumberStructureComponent,
    PrimitiveStructureComponent,
    SequenceStructureComponent,
    SerializerComponent,
    StringStructureComponent,
    RangeVersionTagAutoAssignerComponent,
    StructureBaseComponent,
    StructureTagComponent,
    SwitchStructureComponent,
    TablifierComponent,
    TypeAliasComponent,
    UnionStructureComponent,
    VersionComponent,
    VersionFileComponent,
    VersionFileTypeComponent,
    VersionTagComponent,
    VersionTagOrderComponent,
]
