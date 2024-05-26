import DataMiners.DataMinerTyping as DataMinerTyping
import Structure.StructureEnvironment as StructureEnvironment


class DataMinerEnvironment():

    def __init__(self, dependency_data:DataMinerTyping.DependenciesTypedDict, structure_environment:StructureEnvironment.StructureEnvironment) -> None:
        self.dependency_data = dependency_data
        self.structure_environment = structure_environment
