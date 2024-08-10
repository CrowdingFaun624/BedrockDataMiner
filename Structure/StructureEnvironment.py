import enum
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate
    import Version.Version as Version

class EnvironmentType(enum.Enum):
    all_datamining = "all_datamining"
    checking_types = "checking_types"
    comparing = "comparing"
    datamining = "datamining"

class StructureEnvironment():

    def __init__(self, environment:EnvironmentType) -> None:
        self.environment = environment
        self.should_cache = environment == EnvironmentType.comparing

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

    def __repr__(self) -> str:
        return "<%s %r %r branch %i>" % (self.__class__.__name__, self.version, self.structure_environment, self.branch)

class ComparisonEnvironment():

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        default_delegate:Union["Delegate.Delegate", None],
        version1:Union["Version.Version", None],
        version2:"Version.Version",
        versions_between:list["Version.Version"],
    ) -> None:
        self.structure_environment = structure_environment
        self.default_delegate = default_delegate
        self.version1 = version1
        self.version2 = version2
        self.versions_between = versions_between
        self.printer_environments = [PrinterEnvironment(structure_environment, default_delegate, version, branch) for branch, version in enumerate((version1, version2))]

    def __getitem__(self, branch:int) -> "PrinterEnvironment":
        return self.printer_environments[branch]

    def __repr__(self) -> str:
        return "<%s %r %r %r w/ %i between>" % (self.__class__.__name__, self.version1, self.version2, self.structure_environment, len(self.versions_between))
