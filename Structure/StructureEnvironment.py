import enum
from typing import TYPE_CHECKING

import Domain.Domain as Domain
from Component.Types import register_decorator
from Structure.StructureInfo import StructureInfo
from Utilities.Exceptions import AttributeNoneError

if TYPE_CHECKING:
    from Version.Version import Version

class EnvironmentType(enum.Enum):
    all_datamining = "all_datamining"
    checking_all_types = "checking_all_types"
    checking_types = "checking_types"
    comparing = "comparing"
    datamining = "datamining"
    garbage_collection = "garbage_collection"
    similarity_testing = "similarity_testing"
    uses = "uses"

class StructureEnvironment():

    __slots__ = (
        "domain",
        "environment",
        "should_cache",
    )

    def __init__(self, environment:EnvironmentType, domain:"Domain.Domain") -> None:
        self.environment = environment
        self.should_cache = environment in (EnvironmentType.comparing, EnvironmentType.garbage_collection, EnvironmentType.checking_all_types, EnvironmentType.uses)
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.environment.name} {"caching" if self.should_cache else "uncaching"}>"

    def __hash__(self) -> int:
        return hash((self.environment, self.domain))

@register_decorator(None, lambda data, type_stuff: hash(data)) # need this for hashing in CacheStructure
class PrinterEnvironment():

    __slots__ = (
        "domain",
        "structure_environment",
        "structure_info",
        "version",
        "branch",
    )

    def __init__(
        self,
        structure_environment:StructureEnvironment,
        structure_info:StructureInfo,
        version:"Version",
        branch:int,
    ) -> None:
        self.structure_environment = structure_environment
        self.structure_info = structure_info
        self.domain = self.structure_environment.domain
        self.version = version
        self.branch = branch

    def get_version(self) -> "Version":
        """
        Returns this PrinterEnvironment's Version. Raises an error if it is None.
        """
        if self.version is None:
            raise AttributeNoneError("version", self)
        return self.version

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.version} {self.structure_environment} branch {self.branch}>"

    def __hash__(self) -> int:
        # self.version is excluded
        return hash((self.structure_environment, self.structure_info, self.branch))

class ComparisonEnvironment():

    __slots__ = (
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
        versions:list[tuple["Version",StructureInfo]],
        versions_between:list[list["Version"]], # has a length of len(versions) - 1
    ) -> None:
        self.structure_environment = structure_environment
        self.domain = self.structure_environment.domain
        self.versions = tuple(version[0] for version in versions)
        self.structure_infos = tuple(version[1] for version in versions)
        self.versions_between = versions_between
        self.printer_environments = [PrinterEnvironment(structure_environment, structure_info, version, branch) for branch, (version, structure_info) in enumerate(versions)]

    def __getitem__(self, branch:int) -> "PrinterEnvironment":
        return self.printer_environments[branch]

    def __len__(self) -> int:
        return len(self.versions)

    def __repr__(self) -> str:
        if len(self.versions) <= 5:
            return f"<{self.__class__.__name__} [{", ".join(f"\"{version.name}\"" if version is not None else "None" for version in self.versions)}]>"
        else:
            return f"<{self.__class__.__name__} of {len(self.versions)} versions>"

    def __hash__(self) -> int:
        # versions are excluded
        return hash((self.structure_environment, self.structure_infos))
