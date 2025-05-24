import enum
from typing import TYPE_CHECKING

import Structure.StructureInfo as StructureInfo
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Domain.Domain as Domain
    import Structure.Delegate.Delegate as Delegate
    import Version.Version as Version

class EnvironmentType(enum.Enum):
    all_datamining = "all_datamining"
    checking_all_types = "checking_all_types"
    checking_types = "checking_types"
    comparing = "comparing"
    datamining = "datamining"
    garbage_collection = "garbage_collection"
    similarity_testing = "similarity_testing"

class StructureEnvironment():

    __slots__ = (
        "domain",
        "environment",
        "should_cache",
    )

    def __init__(self, environment:EnvironmentType, domain:"Domain.Domain") -> None:
        self.environment = environment
        self.should_cache = environment in (EnvironmentType.comparing, EnvironmentType.garbage_collection, EnvironmentType.checking_all_types)
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.environment.name} {"caching" if self.should_cache else "uncaching"}>"

class PrinterEnvironment():

    __slots__ = (
        "domain",
        "structure_environment",
        "structure_info",
        "default_delegate",
        "version",
        "branch",
    )

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        structure_info:StructureInfo.StructureInfo,
        default_delegate:"Delegate.Delegate|None",
        version:"Version.Version",
        branch:int,
    ) -> None:
        self.structure_environment = structure_environment
        self.structure_info = structure_info
        self.domain = self.structure_environment.domain
        self.default_delegate = default_delegate
        self.version = version
        self.branch = branch

    def get_version(self) -> "Version.Version":
        '''Returns this PrinterEnvironment's Version. Raises an error if it is None.'''
        if self.version is None:
            raise Exceptions.AttributeNoneError("version", self)
        return self.version

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.version} {self.structure_environment} branch {self.branch}>"

class ComparisonEnvironment():

    __slots__ = (
        "default_delegate",
        "domain",
        "is_multi_diff",
        "printer_environments",
        "structure_environment",
        "structure_infos",
        "versions",
        "versions_between",
    )

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        default_delegate:"Delegate.Delegate|None",
        versions:list[tuple["Version.Version",StructureInfo.StructureInfo]],
        versions_between:list[list["Version.Version"]], # has a length of len(versions) - 1
    ) -> None:
        self.structure_environment = structure_environment
        self.domain = self.structure_environment.domain
        self.default_delegate = default_delegate
        self.versions = [version[0] for version in versions]
        self.structure_infos = [version[1] for version in versions]
        self.versions_between = versions_between
        self.printer_environments = [PrinterEnvironment(structure_environment, structure_info, default_delegate, version, branch) for branch, (version, structure_info) in enumerate(versions)]

    def __getitem__(self, branch:int) -> "PrinterEnvironment":
        return self.printer_environments[branch]

    def __repr__(self) -> str:
        if len(self.versions) <= 5:
            return f"<{self.__class__.__name__} [{", ".join(f"\"{version.name}\"" if version is not None else "None" for version in self.versions)}]>"
        else:
            return f"<{self.__class__.__name__} of {len(self.versions)} versions>"
