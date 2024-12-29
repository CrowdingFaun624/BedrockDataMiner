from typing import Any

import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerSettings as DataMinerSettings
import Domain.Domain as Domain
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Version.Version as Version

NoneType = type(None)

class DataMinerCollection(AbstractDataMinerCollection.AbstractDataMinerCollection):

    def __init__(self, file_name:str, name:str, domain:"Domain.Domain", comparing_disabled:bool) -> None:
        super().__init__(file_name, name, domain, comparing_disabled)

        self.dataminer_settings:list["DataMinerSettings.DataMinerSettings"]|None = None

    def link_subcomponents(self, structure:StructureBase.StructureBase, dataminer_settings:list["DataMinerSettings.DataMinerSettings"]) -> None:
        super().link_subcomponents(structure)
        self.dataminer_settings = dataminer_settings

    def get_dependencies(self, version: Version.Version) -> list[AbstractDataMinerCollection.AbstractDataMinerCollection]:
        return self.get_dataminer_settings(version).get_dependencies()

    def datamine(self, version: Version.Version, environment: DataMinerEnvironment.DataMinerEnvironment) -> Any:
        return self.get_dataminer(version).activate(environment)

    def get_all_dataminer_settings(self) -> list["DataMinerSettings.DataMinerSettings"]:
        if self.dataminer_settings is None:
            raise Exceptions.AttributeNoneError("dataminer_settings", self)
        return self.dataminer_settings

    def get_dataminer_settings(self, version:Version.Version) -> "DataMinerSettings.DataMinerSettings":
        '''Returns a DataMinerSettings such that `version` is in the dataminer's VersionRange'''
        for dataminer_setting in self.get_all_dataminer_settings():
            if version in dataminer_setting.get_version_range():
                return dataminer_setting
        else: raise Exceptions.InvalidStateError("Version matches no DataMinerSettings!")

    def get_dataminer_class(self, version:Version.Version) -> type[DataMiner.DataMiner]:
        '''Returns a type of DataMiner such that `version` is in the dataminer's VersionRange.'''
        dataminer_settings = self.get_dataminer_settings(version)
        return dataminer_settings.get_dataminer_class()

    def get_dataminer(self, version:Version.Version) -> DataMiner.DataMiner:
        '''Returns a DataMiner such that `version` is in the dataminer's VersionRange.'''
        dataminer_settings = self.get_dataminer_settings(version)
        return dataminer_settings.get_dataminer_class()(version, dataminer_settings)

    def supports_version(self, version:Version.Version) -> bool:
        dataminer_settings = self.get_dataminer_settings(version)
        if dataminer_settings.dataminer_class is DataMiner.NullDataMiner:
            return False
        version_files = set(version_file.get_version_file_type() for version_file in version.get_version_files() if version_file.has_accessors())
        return all(
            required_version_file_type in version_files # cannot only datamine it if required files are accessible
            for required_version_file_type in dataminer_settings.get_version_file_types()
        ) and all(
            dependency.supports_version(version)
            for dependency in dataminer_settings.get_dependencies()
        )
