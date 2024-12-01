import enum
from typing import TYPE_CHECKING, Union

import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
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

    def __init__(self, environment:EnvironmentType) -> None:
        self.environment = environment
        self.should_cache = environment in (EnvironmentType.comparing, EnvironmentType.garbage_collection, EnvironmentType.checking_all_types)

    def __repr__(self) -> str:
        return "<%s %s %s>" % (
            self.__class__.__name__,
            self.environment.name,
            "caching" if self.should_cache else "uncaching",
        )

class PrinterEnvironment():

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        default_delegate:Union["Delegate.Delegate", None],
        version:Union["Version.Version", None],
        branch:int,
    ) -> None:
        self.structure_environment = structure_environment
        self.default_delegate = default_delegate
        self.version = version
        self.branch = branch

    def get_version(self) -> "Version.Version":
        '''Returns this PrinterEnvironment's Version. Raises an error if it is None.'''
        if self.version is None:
            raise Exceptions.AttributeNoneError("version", self)
        return self.version

    def __repr__(self) -> str:
        return "<%s %r %r branch %i>" % (self.__class__.__name__, self.version, self.structure_environment, self.branch)

class ComparisonEnvironment():

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        default_delegate:Union["Delegate.Delegate", None],
        versions:list[Union["Version.Version", None]]|list["Version.Version"],
        versions_between:list[list["Version.Version"]], # has a length of len(versions) - 1
        is_multi_diff:bool
    ) -> None:
        self.structure_environment = structure_environment
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
            return "<%s [%s]>" % (self.__class__.__name__, ", ".join("\"%s\"" % (version.name,) if version is not None else "None" for version in self.versions))
        else:
            return "<%s of %i versions>" % (self.__class__.__name__, len(self.versions))
