import enum


class EnvironmentType(enum.Enum):
    all_datamining = "all_datamining"
    checking_types = "checking_types"
    comparing = "comparing"
    datamining = "datamining"

class StructureEnvironment():

    def __init__(self, environment:EnvironmentType) -> None:
        self.environment = environment
        self.should_cache = environment == EnvironmentType.comparing
