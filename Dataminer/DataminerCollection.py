from typing import Any, Iterable, Sequence

from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.DataminerSettings import DataminerSettings
from Structure.StructureInfo import StructureInfo
from Utilities.Exceptions import InvalidStateError
from Version.Version import Version


class DataminerCollection(AbstractDataminerCollection):

    __slots__ = (
        "dataminer_settings",
    )

    def link_dataminer_collection(self, dataminer_settings:Sequence["DataminerSettings"]) -> None:
        self.dataminer_settings:Sequence["DataminerSettings"] = dataminer_settings

    def get_structure_info(self, version: Version) -> StructureInfo:
        return self.get_dataminer_settings(version).structure_info

    def get_required_dependencies(self, version: Version) -> Iterable[AbstractDataminerCollection]:
        return self.get_dataminer_settings(version).dependencies

    def get_optional_dependencies(self, version: Version) -> Iterable[AbstractDataminerCollection]:
        return self.get_dataminer_settings(version).optional_dependencies

    def datamine(self, version: Version, environment: DataminerEnvironment) -> Any:
        return self.get_dataminer(version).activate(environment)

    def get_dataminer_settings(self, version:Version) -> "DataminerSettings":
        '''Returns a DataminerSettings such that `version` is in the dataminer's VersionRange'''
        for dataminer_setting in self.dataminer_settings:
            if version in dataminer_setting.version_range:
                return dataminer_setting
        else: raise InvalidStateError("Version matches no DataminerSettings!")

    def get_dataminer_class(self, version:Version) -> type[Dataminer]:
        '''Returns a type of Dataminer such that `version` is in the dataminer's VersionRange.'''
        dataminer_settings = self.get_dataminer_settings(version)
        dataminer_class = dataminer_settings.get_dataminer_class()
        if dataminer_class is None:
            raise InvalidStateError(self, version, dataminer_class)
        return dataminer_class

    def get_dataminer(self, version:Version) -> Dataminer:
        '''Returns a Dataminer such that `version` is in the dataminer's VersionRange.'''
        dataminer_settings = self.get_dataminer_settings(version)
        dataminer_class = dataminer_settings.get_dataminer_class()
        if dataminer_class is None:
            raise InvalidStateError(self, version, dataminer_class)
        return dataminer_class(version, dataminer_settings)

    def supports_version(self, version:Version) -> bool:
        dataminer_settings = self.get_dataminer_settings(version)
        if dataminer_settings.dataminer_class is None:
            return False
        version_files = set(version_file.version_file_type for version_file in version.version_files if version_file.has_accessors())
        return all(
            required_version_file_type in version_files # cannot only datamine it if required files are accessible
            for required_version_file_type in dataminer_settings.version_file_types
        ) and all(
            dependency.supports_version(version)
            for dependency in dataminer_settings.dependencies # does not contain optional dependencies
        )
