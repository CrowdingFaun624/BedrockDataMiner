import enum
from typing import TYPE_CHECKING

import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Domain.Domain as Domain
    import Structure.Delegate.Delegate as Delegate
    import Version.Version as Version

class EnvironmentType(enum.Enum):
    all_datamining = "all_datamining"
    checking_types = "checking_types"
    comparing = "comparing"
    datamining = "datamining"
    garbage_collection = "garbage_collection"
    checking_all_types = "checking_all_types"

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
        "default_delegate",
        "version",
        "branch",
    )

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        default_delegate:"Delegate.Delegate|None",
        version:"Version.Version|None",
        branch:int,
    ) -> None:
        self.structure_environment = structure_environment
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
        "versions",
        "versions_between",
    )

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        default_delegate:"Delegate.Delegate|None",
        versions:list["Version.Version|None"]|list["Version.Version"],
        versions_between:list[list["Version.Version"]], # has a length of len(versions) - 1
        is_multi_diff:bool
    ) -> None:
        self.structure_environment = structure_environment
        self.domain = self.structure_environment.domain
        self.default_delegate = default_delegate
        self.versions = versions
        self.versions_between = versions_between
        self.printer_environments = [PrinterEnvironment(structure_environment, default_delegate, version, branch) for branch, version in enumerate(versions)]
        self.is_multi_diff = is_multi_diff # if the data1 of comparison may contain diffs.

    def get_first_version(self) -> "Version.Version":
        '''
        Returns the first Version that is not None.
        '''
        for version in self.versions:
            if version is not None:
                return version
        else:
            raise Exceptions.ComparisonEnvironmentNoVersionError(self)

    def get_non_none_versions(self) -> tuple["Version.Version",...]:
        '''
        Returns all items of versions that are not None.
        '''
        return tuple(version for version in self.versions if version is not None)

    def __getitem__(self, branch:int) -> "PrinterEnvironment":
        return self.printer_environments[branch]

    def __repr__(self) -> str:
        if len(self.versions) <= 5:
            return f"<{self.__class__.__name__} [{", ".join(f"\"{version.name}\"" if version is not None else "None" for version in self.versions)}]>"
        else:
            return f"<{self.__class__.__name__} of {len(self.versions)} versions>"
